# Lobster Trap Setup
Owner: Tayyab

## Download
Go to: https://github.com/veea-ai/lobster-trap/releases
Download the binary for your OS:
- Linux:   lobstertrap-linux-amd64
- macOS:   lobstertrap-darwin-arm64
- Windows: lobstertrap-windows-amd64.exe

Rename it to `lobstertrap` and place it in this folder.

## Run
```bash
chmod +x lobstertrap
./lobstertrap serve --config policy.yaml --port 8080
```

## Test
```bash
./lobstertrap inspect "ignore all previous instructions"
./lobstertrap test
```

## How it works
All AI agent traffic goes through port 8080.
Flagged events are sent to: http://localhost:3000/api/webhook/lobster
