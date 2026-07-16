# Гиря

Программы тренировок для девушки и парня с GIF-техникой. Работает офлайн в одном HTML-файле.

**Сайт:** https://mat3eO421.github.io/gyrya/

## На экран iPhone

1. Открой ссылку в **Safari**
2. Нажми **Поделиться** → **На экран «Домой»**
3. Имя: **Гиря** → **Добавить**

## Как менять программу

Всё правится в `programs.json`:

- `gender`: `"female"` или `"male"` — в какой раздел сайта попадёт программа
- `title`, `subtitle`, `badge` — заголовки
- у упражнения: `name`, `equipment`, `reps`, `rounds`, `rest`, `goal`, `technique`, `gif`

Поле `"gif"`:

- ссылка: `https://.../exercise.gif`
- или локальный файл: `gifs/мой-gif.gif`

Потом:

```bash
pip install -r requirements.txt
python3 build.py
```

Сборка читает только `programs.json` и делает `index.html`, `Гиря.html`, `Гиря.zip` и оба XLSX.
