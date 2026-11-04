export function apply(ctx) {
  try {
    if (!ctx || typeof ctx.effect !== 'function') {
      return () => {};
    }

    return ctx.effect(() => {
      try {
        const webServer = ctx.get('webServer');
        if (!webServer || typeof webServer.register !== 'function') {
          return () => {};
        }

        const handler = async (request) => {
          try {
            const body = await request.json();
            const count = Math.max(1, Math.min(50, Number(body.count || 5)));
            const root = 'C:\\Users\\Mateusz\\Desktop\\vault';
            const out = `${root}\\scripts\\_scratch\\sessions\\02_products\\last_sessions_exact.md`;

            const { execFile } = await import('node:child_process');
            const { promisify } = await import('node:util');
            const execFileAsync = promisify(execFile);
            const { readFile } = await import('node:fs/promises');
            const path = await import('node:path');

            await execFileAsync('python', [
              path.join(root, 'scripts', 'extract_exact_sessions.py'),
              '--count',
              String(count),
              '--out',
              out,
            ], { cwd: root, windowsHide: true, timeout: 120000 });

            const markdown = await readFile(out, 'utf8');
            const response = await fetch('https://mdshare.live/api/documents', {
              method: 'POST',
              headers: { 'Content-Type': 'text/markdown' },
              body: markdown,
            });

            const result = await response.json();
            return new Response(JSON.stringify(result), {
              headers: { 'Content-Type': 'application/json' },
            });
          } catch (error) {
            return new Response(JSON.stringify({ error: String(error) }), {
              status: 500,
              headers: { 'Content-Type': 'application/json' },
            });
          }
        };

        const dispose = webServer.register({
          method: 'POST',
          path: '/__plugins/mdshare-sessions/share',
          handler,
        });

        return dispose;
      } catch (error) {
        console.error('[mdshare-sessions] effect error:', error);
        return () => {};
      }
    });
  } catch (error) {
    console.error('[mdshare-sessions] apply error:', error);
    return () => {};
  }
}
