# Fairy-Stockfish Discord Bot

A self-contained Discord bot that checks `variants.ini` files using Fairy-Stockfish.

## Features

- Accepts `.ini` file uploads or inline text via `!check`
- Uses Fairy-Stockfish's `check` command
- Fully self-contained, builds FSF via Docker
- Deployable on [Render](https://render.com)

## Usage

In any Discord channel:

### Upload a file
```
!check
[attach variants.ini]
```

### Inline input
```
!check
[myvariant]
option = value
```

## Deployment on Render

1. Push this repo to GitHub.
2. Go to Render.com → Create a new **Background Worker**.
3. Choose "Docker" as environment.
4. Add environment variable: `DISCORD_BOT_TOKEN`
5. Deploy!

## Notes

- FSF is compiled from source inside the container.
- Output is truncated to fit within Discord message limits.
