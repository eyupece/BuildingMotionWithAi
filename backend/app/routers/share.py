import logging
import os
import tempfile

import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse

from ..config import settings
from ..models.schemas import ShareResponse, ShareStatusResponse
from ..services import storage_service, veo_service
from ..services.video_utils import compose_videos_side_by_side
from .upload import _base_url

logger = logging.getLogger(__name__)

# JSON API endpoint — mounted with /api prefix → /api/share/{video_id}
router = APIRouter()

# HTML share page — mounted without prefix → /share/{video_id}
html_router = APIRouter()


def _get_or_compose(video_id: str) -> str:
    """Return a 24hr signed URL for the composed video, composing it if needed.

    Returns a signed GCS URL string.
    Raises HTTPException on missing video or composition failure.
    """
    # 1. In-memory cache hit — fastest path
    if video_id in storage_service._composed_cache:
        gcs_uri = storage_service._composed_cache[video_id]
        return storage_service.generate_video_signed_url(gcs_uri)

    # 2. Composed video already in GCS (survives server restarts)
    composed_gcs_uri = f"gs://{settings.GCS_BUCKET}/output/{video_id}/composed.mp4"
    if storage_service.gcs_blob_exists(composed_gcs_uri):
        storage_service._composed_cache[video_id] = composed_gcs_uri
        return storage_service.generate_video_signed_url(composed_gcs_uri)

    # 3. Need to compose — find the trimmed generated video
    trimmed_gcs_uri = veo_service.get_completed_video_uri(video_id)
    if not trimmed_gcs_uri:
        # Server may have restarted — check GCS directly for the trimmed video
        trimmed_gcs_uri = f"gs://{settings.GCS_BUCKET}/output/{video_id}/trimmed_3s.mp4"
        if not storage_service.gcs_blob_exists(trimmed_gcs_uri):
            raise HTTPException(
                status_code=404,
                detail=f"No completed video found for video_id={video_id}",
            )

    # MOCK_AI: skip composition, return mock signed URL
    if settings.MOCK_AI:
        mock_uri = f"gs://{settings.GCS_BUCKET}/output/{video_id}/composed.mp4"
        storage_service._composed_cache[video_id] = mock_uri
        return storage_service.generate_video_signed_url(mock_uri)

    original_path: str | None = None
    generated_path: str | None = None
    composed_path: str | None = None

    try:
        # Download original webm
        original_gcs = f"gs://{settings.GCS_BUCKET}/uploads/{video_id}.webm"
        original_path = storage_service.download_to_temp(original_gcs, video_id)

        # Download trimmed generated mp4
        generated_path = storage_service.download_gcs_video(trimmed_gcs_uri)

        # Compose 9:16 vertical video
        composed_path = compose_videos_side_by_side(original_path, generated_path)

        # Upload to GCS and cache
        with open(composed_path, "rb") as f:
            composed_data = f.read()

        gcs_uri = storage_service.upload_composed_video(video_id, composed_data)
        storage_service._composed_cache[video_id] = gcs_uri

        return storage_service.generate_video_signed_url(gcs_uri)

    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Composition failed for video_id=%s: %s", video_id, exc)
        raise HTTPException(status_code=500, detail=f"Video composition failed: {exc}") from exc
    finally:
        for path in (original_path, generated_path, composed_path):
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except OSError:
                    pass


def _avatar_video_url(video_id: str) -> str | None:
    """Signed URL for the AI video on its own (the bottom half of the share video)."""
    uri = f"gs://{settings.GCS_BUCKET}/output/{video_id}/trimmed_3s.mp4"
    try:
        if storage_service.gcs_blob_exists(uri):
            return storage_service.generate_video_signed_url(uri)
    except Exception:  # noqa: BLE001
        pass
    return None


@router.get("/share/{video_id}", response_model=ShareResponse)
async def get_share(video_id: str, request: Request):
    """Return download URL for the composed video and a share page URL for the QR code."""
    try:
        signed_url = _get_or_compose(video_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate share URL: {exc}") from exc

    share_page_url = f"{_base_url(request)}/share/{video_id}"
    return ShareResponse(download_url=signed_url, qr_data=share_page_url)


@router.get("/share/{video_id}/download")
async def download_video(video_id: str, v: str = ""):
    """Same-origin proxy that streams the composed video with attachment headers.

    This fixes iOS Safari which ignores the HTML5 `download` attribute on
    cross-origin links (GCS signed URLs live on storage.googleapis.com).
    Works on all platforms: iOS Safari, Android Chrome, desktop browsers.
    """
    filename = "building-motion-with-ai.mp4"
    try:
        if v == "avatar":
            signed_url = _avatar_video_url(video_id)
            if not signed_url:
                raise HTTPException(status_code=404, detail="Avatar video not found")
            filename = "building-motion-with-ai-avatar.mp4"
        else:
            signed_url = _get_or_compose(video_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Download failed: {exc}") from exc

    async def _stream():
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", signed_url) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes(chunk_size=64 * 1024):
                    yield chunk

    return StreamingResponse(
        _stream(),
        media_type="video/mp4",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.get("/share/{video_id}/status", response_model=ShareStatusResponse)
async def get_share_status(video_id: str):
    """Check video readiness — returns stage: generating | composing | ready."""

    def _get_avatar_url(vid: str) -> str | None:
        """Try to get a signed URL for the avatar image."""
        # Poster kit: the still with the poster around it is the nicer keepsake
        for name in (f"{vid}-poster", vid):
            avatar_gcs = f"gs://{settings.GCS_BUCKET}/avatars/{name}.png"
            try:
                if storage_service.gcs_blob_exists(avatar_gcs):
                    return storage_service.generate_signed_url(avatar_gcs, vid)
            except Exception:  # noqa: BLE001
                pass
        return None

    # 1. Already composed? → ready
    if video_id in storage_service._composed_cache:
        gcs_uri = storage_service._composed_cache[video_id]
        try:
            signed_url = storage_service.generate_video_signed_url(gcs_uri)
            return ShareStatusResponse(
                stage="ready",
                download_url=signed_url,
                avatar_url=_get_avatar_url(video_id),
                avatar_video_url=_avatar_video_url(video_id),
            )
        except Exception:  # noqa: BLE001
            pass

    composed_gcs_uri = f"gs://{settings.GCS_BUCKET}/output/{video_id}/composed.mp4"
    if storage_service.gcs_blob_exists(composed_gcs_uri):
        storage_service._composed_cache[video_id] = composed_gcs_uri
        try:
            signed_url = storage_service.generate_video_signed_url(composed_gcs_uri)
            return ShareStatusResponse(
                stage="ready",
                download_url=signed_url,
                avatar_url=_get_avatar_url(video_id),
                avatar_video_url=_avatar_video_url(video_id),
            )
        except Exception:  # noqa: BLE001
            pass

    # 2. Trimmed or raw Veo output exists? → composing
    trimmed_gcs_uri = f"gs://{settings.GCS_BUCKET}/output/{video_id}/trimmed_3s.mp4"
    if storage_service.gcs_blob_exists(trimmed_gcs_uri):
        return ShareStatusResponse(stage="composing")

    raw_uri = veo_service.get_completed_video_uri(video_id)
    if raw_uri:
        return ShareStatusResponse(stage="composing")

    # 3. Nothing yet → generating
    return ShareStatusResponse(stage="generating")


@html_router.get("/share/{video_id}", response_class=HTMLResponse)
async def share_page(video_id: str):
    """Serve the mobile share landing page with stage-aware polling."""
    try:
        return _render_share_page(video_id)
    except Exception as exc:
        logger.exception("share_page failed for video_id=%s", video_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def _render_share_page(video_id: str) -> HTMLResponse:
    html = (
        _SHARE_PAGE
        .replace("__STATUS_URL__", f"/api/share/{video_id}/status")
        .replace("__DOWNLOAD_URL__", f"/api/share/{video_id}/download")
    )
    return HTMLResponse(content=html)


# Plain template instead of an f-string, so the CSS and JS braces stay readable
_SHARE_PAGE = """<!DOCTYPE html>
<html lang="tr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <meta name="theme-color" content="#F8FAFD">
  <title>Building Motion with AI</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #F8FAFD; color: #202124;
      font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      min-height: 100dvh; display: flex; flex-direction: column; align-items: center;
      padding: 20px 16px calc(env(safe-area-inset-bottom, 0px) + 24px); gap: 18px;
    }
    .brand { display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 0.95rem; }
    .dots { display: flex; gap: 4px; }
    .dots i { width: 8px; height: 8px; border-radius: 50%; display: block; }
    h1 { font-size: 1.6rem; font-weight: 700; text-align: center; letter-spacing: -0.01em; }
    p.sub { color: #5F6368; font-size: 0.95rem; text-align: center; margin-top: -10px; }
    .card {
      width: 100%; max-width: 340px; background: #fff; border-radius: 24px; padding: 8px;
      box-shadow: 0 1px 2px rgba(60,64,67,0.08), 0 8px 24px rgba(60,64,67,0.10);
    }
    video { width: 100%; display: block; border-radius: 18px; background: #202124; aspect-ratio: 9/16; object-fit: cover; }
    .buttons { display: flex; flex-direction: column; gap: 10px; width: 100%; max-width: 340px; }
    .btn {
      display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%;
      padding: 15px; border-radius: 999px; font: inherit; font-size: 1rem; font-weight: 700;
      border: none; cursor: pointer; text-decoration: none; -webkit-tap-highlight-color: transparent;
    }
    .btn-primary { background: #1A73E8; color: #fff; }
    .btn-secondary { background: #fff; color: #1A73E8; border: 1px solid #DADCE0; }
    .btn[disabled] { opacity: 0.6; }
    .avatar { display: flex; align-items: center; gap: 14px; width: 100%; max-width: 340px; padding: 10px;
      background: #fff; border-radius: 18px; border: 1px solid #E8EAED; }
    .avatar img { width: 64px; height: 64px; border-radius: 12px; object-fit: cover; }
    .avatar h3 { font-size: 0.95rem; font-weight: 700; }
    .avatar p { color: #5F6368; font-size: 0.85rem; }
    .avatar a { margin-left: auto; color: #1A73E8; font-weight: 700; font-size: 0.9rem; text-decoration: none; }
    .loading { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 36px 16px; text-align: center; }
    .spinner { width: 44px; height: 44px; border: 4px solid #E8EAED; border-top-color: #1A73E8; border-radius: 50%;
      animation: spin 1s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }
    .msg { color: #5F6368; font-size: 0.95rem; line-height: 1.5; }
    .hint { color: #9AA0A6; font-size: 0.82rem; line-height: 1.5; }
    .switch { display: flex; width: 100%; max-width: 340px; padding: 4px; background: #E8EAED; border-radius: 999px; }
    .switch button { flex: 1; padding: 10px; border: none; border-radius: 999px; background: none; font: inherit;
      font-size: 0.9rem; font-weight: 700; color: #5F6368; cursor: pointer; -webkit-tap-highlight-color: transparent; }
    .switch button.on { background: #fff; color: #1A73E8; box-shadow: 0 1px 3px rgba(60,64,67,0.2); }
    video.fit { object-fit: contain; }
    .hidden { display: none !important; }
    footer { color: #9AA0A6; font-size: 0.78rem; margin-top: auto; text-align: center; }
  </style>
</head>
<body>
  <div class="brand">
    <span class="dots"><i style="background:#4285F4"></i><i style="background:#EA4335"></i><i style="background:#FBBC04"></i><i style="background:#34A853"></i></span>
    Building Motion with AI
  </div>
  <h1>Videon</h1>
  <p class="sub">Aynı hareket, yeni sen.</p>

  <div id="loading-state" class="loading">
    <div class="spinner"></div>
    <p id="stage-text" class="msg">Video yapay zekayla oluşturuluyor.<br>Genelde 1-2 dakika sürüyor.</p>
    <p id="elapsed" class="hint" style="font-variant-numeric:tabular-nums"></p>
    <p class="hint">Bu sayfayı açık bırakabilirsin,<br>video hazır olunca kendiliğinden açılacak.</p>
  </div>

  <div id="timeout-state" class="loading hidden">
    <div style="font-size:2.6rem">&#x23F0;</div>
    <p style="font-weight:700;font-size:1.05rem">Video bulunamadı</p>
    <p class="msg">Oturum sona ermiş olabilir.<br>Standa dönüp tekrar kaydedebilirsin.</p>
  </div>

  <div id="variant" class="switch hidden">
    <button type="button" class="on" data-v="both">Benimle birlikte</button>
    <button type="button" data-v="avatar">Sadece avatar</button>
  </div>

  <div id="ready-state" class="card hidden">
    <video id="main-video" autoplay loop playsinline muted controls></video>
  </div>

  <div id="action-buttons" class="buttons hidden">
    <button class="btn btn-primary hidden" id="share-btn" type="button">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M4 12v7a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-7"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
      Paylaş
    </button>
    <a class="btn btn-secondary" id="download-link" href="#" download="building-motion-with-ai.mp4">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      Videoyu indir
    </a>
  </div>

  <div id="avatar-section" class="avatar hidden">
    <img id="avatar-img" src="" alt="Avatarın">
    <div>
      <h3>Avatarın</h3>
      <p>Nano Banana çizdi</p>
    </div>
    <a id="avatar-download-link" href="#" download="avatar.png" target="_blank" rel="noopener">İndir</a>
  </div>

  <footer>DevFest &middot; Gemini, Nano Banana ve Veo ile yapıldı</footer>

  <script>
    const STATUS_URL = "__STATUS_URL__";
    const DOWNLOAD_URL = "__DOWNLOAD_URL__";
    const stageText = document.getElementById('stage-text');
    const elapsedEl = document.getElementById('elapsed');
    const startTime = Date.now();

    const STAGE_MESSAGES = {
      generating: 'Video yapay zekayla oluşturuluyor.<br>Genelde 1-2 dakika sürüyor.',
      composing: 'Neredeyse bitti,<br>video hazırlanıyor...',
    };
    const STAGE_TIMEOUTS = { generating: 5 * 60 * 1000, composing: 4 * 60 * 1000 };
    let currentStage = 'generating';
    let stageStartTime = Date.now();

    function formatTime(ms) {
      const s = Math.floor(ms / 1000);
      return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0');
    }

    function showTimeout() {
      document.getElementById('loading-state').classList.add('hidden');
      document.getElementById('timeout-state').classList.remove('hidden');
    }

    async function pollForVideo() {
      while (true) {
        elapsedEl.textContent = 'Geçen süre: ' + formatTime(Date.now() - startTime);
        if (Date.now() - stageStartTime > (STAGE_TIMEOUTS[currentStage] || 5 * 60 * 1000)) {
          showTimeout();
          return;
        }
        try {
          const res = await fetch(STATUS_URL);
          if (res.ok) {
            const data = await res.json();
            if (data.stage === 'ready' && data.download_url) {
              showVideo(data.download_url, data.avatar_url, data.avatar_video_url);
              return;
            }
            if (data.stage !== currentStage) {
              currentStage = data.stage;
              stageStartTime = Date.now();
            }
            if (STAGE_MESSAGES[data.stage]) stageText.innerHTML = STAGE_MESSAGES[data.stage];
          }
        } catch (e) { }
        await new Promise(r => setTimeout(r, 2000));
      }
    }

    // Two versions: the share video (recording on top, AI below) and the AI video alone.
    const variants = { both: { download: DOWNLOAD_URL, name: 'building-motion-with-ai.mp4' } };
    let current = 'both';
    const shareBtn = document.getElementById('share-btn');

    // The phone's own share sheet, so people can pick Instagram, WhatsApp, LinkedIn...
    // Files are fetched up front: iOS only opens the sheet straight from the tap.
    // Until the file is ready (or if the browser can't share files) the page link is shared.
    if (navigator.share) shareBtn.classList.remove('hidden');

    async function prepareShare(key) {
      const v = variants[key];
      if (!navigator.share || !navigator.canShare) return;
      try {
        const res = await fetch(v.download);
        if (!res.ok) return;
        const blob = await res.blob();
        const file = new File([blob], v.name, { type: 'video/mp4' });
        if (navigator.canShare({ files: [file] })) v.file = file;
      } catch (e) { }
    }

    shareBtn.addEventListener('click', async () => {
      const file = variants[current].file;
      try {
        if (file) await navigator.share({ files: [file], title: 'Building Motion with AI' });
        else await navigator.share({ title: 'Building Motion with AI', url: location.href });
      } catch (e) { }
    });

    function pick(key) {
      current = key;
      const v = variants[key];
      const video = document.getElementById('main-video');
      video.src = v.url;
      video.classList.toggle('fit', key === 'avatar');
      document.getElementById('download-link').href = v.download;
      document.getElementById('download-link').setAttribute('download', v.name);
      document.querySelectorAll('#variant button').forEach(b => b.classList.toggle('on', b.dataset.v === key));
    }

    document.querySelectorAll('#variant button').forEach(b => b.addEventListener('click', () => pick(b.dataset.v)));

    function showVideo(url, avatarUrl, avatarVideoUrl) {
      document.getElementById('loading-state').classList.add('hidden');
      document.getElementById('ready-state').classList.remove('hidden');
      document.getElementById('action-buttons').classList.remove('hidden');
      variants.both.url = url;
      if (avatarVideoUrl) {
        variants.avatar = { url: avatarVideoUrl, download: DOWNLOAD_URL + '?v=avatar', name: 'building-motion-with-ai-avatar.mp4' };
        document.getElementById('variant').classList.remove('hidden');
      }
      // download goes through the same-origin proxy so iOS Safari saves the file
      pick('both');
      if (avatarUrl) {
        document.getElementById('avatar-section').classList.remove('hidden');
        document.getElementById('avatar-img').src = avatarUrl;
        document.getElementById('avatar-download-link').href = avatarUrl;
      }
      prepareShare('both');
      if (variants.avatar) prepareShare('avatar');
    }

    pollForVideo();
  </script>
</body>
</html>"""
