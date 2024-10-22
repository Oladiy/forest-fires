# Решение команды tobytes() по кейсу Минприроды РФ

Техническое решение состоит в использовании картинок для построения прогноза возникновения пожара на маске изображения.
В рамках хакатона разработана сверточная сеть, состоящая из энкодера effnet_b3 и декодером для распознавания возможного пожара на спутниковом снимке. Энкодер взят с весами imagenet.
Уникальность решения состоит в спроектированной архитектуре, позволяющей прогнозировать пожар с 4 каналов изображения.

## Структура репозитория
- `api.py` - скрипт для получения дополнительной информации о погоде из нескольких открытых источников.
- `front.py` - скрипт для запуска фронта командой `streamlit run front.py`.
- `json_to_csv.py`, `saturate.py` - скрипты для насыщения моделей дополнительными данными из открытых источников.
- `train_script.ipynb` - `train-скрипт`.

## Валидация решения
Для валидации модели необходимо активировать ячейку с model = smp.Unet(encoder_name="efficientnet-b3", encoder_weights="imagenet", in_channels=4, classes=1) с учетом количества каналов, которые необходимо проанализировать, подгрузить веса. Далее можно перейти в раздел Validation и протестировать решение. Также можно загрузить фронт и попробовать в вебрежиме модель. Фронт доступен только для модели, учитывающей 3 канала изображения (необходимо 3х канальное изображение для подачи в модель)
