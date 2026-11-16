// Screenshots the pages render.py wrote. Prints a line for any overflow or console error.
const { chromium } = require('playwright');

(async () => {
  const out = process.argv[2];
  const names = JSON.parse(process.argv[3]);
  const browser = await chromium.launch();
  let bad = 0;
  for (const name of names) {
    for (const theme of ['light', 'dark']) {
      for (const width of [960, 390]) {
        if (name === 'Cover' && width === 390) continue;
        const page = await browser.newPage({ viewport: { width, height: 300 } });
        const errors = [];
        page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
        await page.goto('file://' + out + '/' + name + '-' + theme + '.html');
        await page.waitForTimeout(2600);
        const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
        await page.screenshot({ path: out + '/' + name + '-' + theme + '-' + width + '.png', fullPage: true });
        if (overflow || errors.length) { bad += 1; console.log(name, theme, width, 'overflow:', overflow, errors.join(' | ')); }
        await page.close();
      }
    }
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
