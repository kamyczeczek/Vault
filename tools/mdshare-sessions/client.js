window.__ModuleLoader__.load({
  id: '@local/mdshare-sessions',
  factory(require) {
    const React = require('react');
    const h = React.createElement;
    const styles = require('styles');
    const css = `.mdss-wrap{display:flex;flex-direction:column;gap:10px;padding:12px 0;max-width:360px}.mdss-btn{border:1px solid var(--dsw-alias-border-primary);background:var(--dsw-alias-background-secondary);color:var(--dsw-alias-text-primary);border-radius:8px;padding:8px 10px;font:inherit;cursor:pointer;text-align:left}.mdss-btn:hover{background:var(--dsw-alias-background-tertiary)}.mdss-input{width:58px;margin-left:8px;background:var(--dsw-alias-background-primary);color:var(--dsw-alias-text-primary);border:1px solid var(--dsw-alias-border-primary);border-radius:6px;padding:4px}.mdss-result{font-size:12px;word-break:break-all;color:var(--dsw-alias-text-secondary)}.mdss-result a{color:var(--dsw-alias-text-link)}`;
    function ShareSessions() {
      const [count, setCount] = React.useState(5);
      const [busy, setBusy] = React.useState(false);
      const [result, setResult] = React.useState(null);
      React.useEffect(() => {
        try { styles.insert(css); } catch (e) { console.error(e); }
      }, []);
      async function run() {
        setBusy(true);
        setResult(null);
        try {
          const response = await fetch('/__plugins/mdshare-sessions/share', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ count }),
          });
          const result = await response.json();
          setResult(result);
        } catch (e) {
          setResult({ ok: false, error: String(e) });
        } finally {
          setBusy(false);
        }
      }
      return h('div', { className:'mdss-wrap', role:'group', 'aria-label':'Share recent sessions' },
        h('button', { className:'mdss-btn', onClick:run, disabled:busy }, busy ? 'Tworzę i wysyłam…' : 'Udostępnij ostatnie sesje'),
        h('label', null, 'Liczba sesji:', h('input', { className:'mdss-input', type:'number', min:1, max:50, value:count, onChange:e=>setCount(Number(e.target.value)||1) })),
        result && (result.ok ? h('div', { className:'mdss-result' }, 'Gotowe: ', h('a', { href:result.url, target:'_blank', rel:'noreferrer' }, result.url)) : h('div', { className:'mdss-result' }, 'Błąd: ', result.error))
      );
    }
    return { inject: ['slots'], apply(ctx) {
      ctx.slots.inject('sidebar.footer.action', () => ctx.slots.register({ name:'sidebar.footer.action', id:'mdshare-sessions', order:20, label:'Udostępnij sesje' }, ShareSessions));
    }};
  }
});
