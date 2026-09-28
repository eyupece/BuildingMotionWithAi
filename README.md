# Building Motion with AI

Bir hareketi anlayan, dönüştüren ve yeniden üreten multimodal AI pipeline'ı.

Bu repo, **Eyüp Ece**'nin DevFest'lerde sunduğu "Building Motion with AI" konuşmasının demo kodu ve sunum materyalleridir. Kısa bir hareket videosu çekiyorsunuz; Gemini hareketi analiz ediyor, Nano Banana sizden bir avatar üretiyor, Veo bu avatarla aynı hareketi yapan yeni bir video oluşturuyor ve sonuç bir QR kodla telefonunuza geliyor.

> **Kaynak:** Kod, Google'ın [Gemini Motion Lab codelab'ine](https://codelabs.developers.google.com/codelabs/gemini-motion-lab/instructions#0) ait [gemini-motion-lab-starter](https://github.com/cuppibla/gemini-motion-lab-starter) reposuna dayanır. Orijinal kodun ve codelab'in yazarı **Qingyue (Annie) Wang**'dir. Commit geçmişi korunmuştur.

## Pipeline

```
Video  →  Gemini analizi  →  Nano Banana avatar  →  Veo video  →  Paylaşılabilir sonuç
(GCS)     (structured JSON)   (referans görsel)      (8 sn, 16:9)   (QR + share sayfası)
```

| Aşama | Ne yapıyor | Kod |
|---|---|---|
| Upload | Tarayıcıda kaydedilen ~5 sn'lik WebM videoyu GCS'e yazar, `video_id` üretir | `backend/app/routers/upload.py`, `services/storage_service.py` |
| Gemini | Hareketi vücut bölümleri, fazlar, tempo ve enerji içeren JSON'a çevirir (MediaPipe poz verisiyle desteklenir) | `services/gemini_service.py`, `services/pose_service.py`, `prompts/motion_analysis.py` |
| Nano Banana | En iyi kareden seçilen stilde avatar üretir | `services/nano_banana_service.py`, `prompts/avatar_generation.py` |
| Veo | Avatar + hareket bilgisinden yeni video üretir | `services/veo_service.py`, `prompts/video_generation.py` |
| Async & kuyruk | Uzun süren işleri arka planda yürütür, frontend durumu poll eder (en fazla 3 eşzamanlı iş) | `services/pipeline.py`, `routers/status.py`, `routers/queue.py` |
| Share | Orijinal + AI videoyu yan yana birleştirir, QR kodlu paylaşım sayfası sunar | `services/video_utils.py`, `routers/share.py` |

Kullanılan modeller: `gemini-3-flash-preview`, `gemini-3.1-flash-image-preview` (Nano Banana), `veo-3.1-fast-generate-001`.

Mimari diyagramlar: [`arch-1-cloud.svg`](arch-1-cloud.svg), [`arch-2-ai-pipeline.svg`](arch-2-ai-pipeline.svg), [`arch-3-kiosk-flow.svg`](arch-3-kiosk-flow.svg), [`arch-4-wallet-share.svg`](arch-4-wallet-share.svg).

## Repo yapısı

```
backend/    FastAPI servisi (Cloud Run)
frontend/   React + Vite + TypeScript kiosk arayüzü (Cloud Run)
talk/       Konuşmanın sunumu
init.sh     GCP projesi oluşturur ve billing bağlar
setup.sh    Service account, GCS bucket ve .env dosyasını hazırlar
codelab.md  Codelab'in tam metni (İngilizce, adım adım)
```

## Kendi projende kurulum

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/eyupece/BuildingMotionWithAi)

Butona tıklarsan repo Cloud Shell'de klonlanmış olarak açılır; 1. adımı atlayıp 2. adımdan devam edebilirsin.

Gereken: faturalandırması açık bir Google Cloud hesabı. En kolayı [Cloud Shell](https://ide.cloud.google.com/) üzerinden çalışmak; `gcloud` orada hazır gelir. Adımların ayrıntılı açıklaması [`codelab.md`](codelab.md) içinde.

**1. Repoyu klonla**

```bash
git clone https://github.com/eyupece/BuildingMotionWithAi.git
cd BuildingMotionWithAi
```

**2. Projeyi oluştur ve API'leri aç**

```bash
chmod +x init.sh setup.sh
./init.sh
gcloud config set project $(cat ~/project_id.txt) --quiet
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  aiplatform.googleapis.com storage.googleapis.com artifactregistry.googleapis.com
```

**3. Kaynakları hazırla ve yetkileri ver**

```bash
./setup.sh
export PROJECT_ID=$(cat ~/project_id.txt)
SA="gemini-motion-lab-sa@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA" --role="roles/storage.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA" --role="roles/aiplatform.user"

PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud iam service-accounts add-iam-policy-binding $SA --project=$PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```

**4. Backend'i Cloud Run'a deploy et**

```bash
source .env
cd backend
gcloud run deploy gemini-motion-lab-backend --source . --region us-central1 \
  --allow-unauthenticated --min-instances 1 --max-instances 3 --memory 2Gi --port 8080 \
  --project $GOOGLE_CLOUD_PROJECT \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GCS_BUCKET=$GCS_BUCKET,GCS_SIGNING_SA=$GCS_SIGNING_SA,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI,MOCK_AI=$MOCK_AI"

BACKEND_URL=$(gcloud run services describe gemini-motion-lab-backend --region us-central1 \
  --format="value(status.url)" --project $GOOGLE_CLOUD_PROJECT)
```

**5. Frontend'i deploy et ve backend'e bağla**

```bash
cd ../frontend
echo "VITE_API_BASE=$BACKEND_URL" > .env
echo "VITE_EVENT=kastamonu" >> .env   # isteğe bağlı: etkinlik seçimi, aşağıya bak
gcloud run deploy gemini-motion-lab-frontend --source . --region us-central1 \
  --allow-unauthenticated --min-instances 1 --max-instances 3 --port 8080 \
  --project $GOOGLE_CLOUD_PROJECT

FRONTEND_URL=$(gcloud run services describe gemini-motion-lab-frontend --region us-central1 \
  --format="value(status.url)" --project $GOOGLE_CLOUD_PROJECT)
gcloud run services update gemini-motion-lab-backend --region us-central1 \
  --update-env-vars PUBLIC_BASE_URL=$FRONTEND_URL --project $GOOGLE_CLOUD_PROJECT

echo "Demo hazır: $FRONTEND_URL"
```

`MOCK_AI=true` ile backend model çağrısı yapmadan sahte sonuç döner; arayüzü maliyetsiz denemek için kullanışlıdır.

> **Maliyet notu:** Veo ve Nano Banana çağrıları ücretlidir. Denemen bittiğinde Cloud Run servislerini ve GCS bucket'ını silmeyi unutma; kodda otomatik silme yok.

## DevFest etkinlikleri

Her DevFest'in kendi avatar stili ve konum teması var. Hepsi `main`'de duruyor; hangisinin görüneceğini frontend'i build ederken `VITE_EVENT` belirler. Seçilen etkinliğin kartları ilk sıraya gelir, diğer şehirlerinkiler gizli kalır ve karşılama ekranında etkinliğin adı yazar. `VITE_EVENT` boşsa orijinal codelab kartları görünür.

| Etkinlik | `VITE_EVENT` | Avatar stili | Konum teması |
|---|---|---|---|
| DevFest Kastamonu 2026 | `kastamonu` | Kastamonu Gravür (sepya gravür, Anadolu kitap illüstrasyonu) | Kastamonu (kale, konaklar, Saat Kulesi, Nasrullah Camii) |
| DevFest Trabzon 2026 | `trabzon` | Rembrandt (17. yüzyıl Hollanda yağlı boya portresi) | Trabzon (Karadeniz limanı, Ayasofya, Sümela, çay bahçeleri) |

Pipeline her etkinlikte aynıdır; etkinlik yalnızca Nano Banana ve Veo prompt'larına giren stil ve konum metnini değiştirir.

**Yeni etkinlik eklemek:**
1. `backend/app/events/` altındaki bir dosyayı kopyala, prompt'ları yaz ve `backend/app/events/__init__.py` içine kaydet.
2. `frontend/src/events.ts` içine kartlarını ekle.
3. İki önizleme görselini (640x640) `frontend/public/previews/` altına koy.

## Sunum

Konuşmanın güncel sunumu: [`talk/BuildingMotionWithAI.pptx`](talk/BuildingMotionWithAI.pptx). Geçişler PowerPoint'in Morph efektiyle hazırlandı; en iyi PowerPoint'te görünür.
