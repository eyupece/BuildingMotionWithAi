# Building Motion with AI

DevFest'lerde anlattığım "Building Motion with AI" konuşmasının demo kodu.

Kameraya birkaç saniyelik bir hareket yapıyorsunuz. Gemini hareketi analiz ediyor, Nano Banana sizden bir avatar çiziyor, Veo da o avatarı aynı hareketi yaparken canlandırıyor. Sonuç QR kodla telefonunuza geliyor.

Kodun temeli Annie Wang'in [Gemini Motion Lab codelab'i](https://codelabs.developers.google.com/codelabs/gemini-motion-lab/instructions#0). Ben üzerine her DevFest'e özel bir tema ekledim.

## Kendin denemek istersen

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/eyupece/BuildingMotionWithAi)

Faturalandırması açık bir Google Cloud hesabı yeterli. Butonla Cloud Shell'de açıp şunları sırayla çalıştırabilirsin:

```bash
./init.sh
gcloud config set project $(cat ~/project_id.txt) --quiet
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  aiplatform.googleapis.com storage.googleapis.com artifactregistry.googleapis.com
./setup.sh
```

IAM yetkileri ve Cloud Run deploy adımları [codelab.md](codelab.md) içinde anlatıldığı gibi. Tek fark şu: frontend'in `.env` dosyasına `VITE_API_BASE` satırını yazdığın adımdan sonra, hangi DevFest'in temasını görmek istediğini de ekleyebilirsin.

```bash
echo "VITE_EVENT=kastamonu" >> frontend/.env   # ya da trabzon
```

Veo ve Nano Banana ücretli. Denemen bitince Cloud Run servislerini ve bucket'ı silmeyi unutma.

## DevFest temaları

Her DevFest'te o şehre ait bir dünya ekleniyor. Avatar stilleri codelab'dekilerle aynı, yani Kastamonu sokaklarında bir Pixel Hero da olabilirsin, 3D figür de.

- **Kastamonu:** Konaklar, kale ve Saat Kulesi.
- **Trabzon:** Çay bahçeleri, liman, Ayasofya ve Sümela.

Şehir prompt'ları `backend/app/events/` klasöründe.

## Sunum

Konuşmanın sunumu [talk/](talk/) klasöründe.
