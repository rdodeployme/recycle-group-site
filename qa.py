import asyncio
from playwright.async_api import async_playwright
PAGES=["/","/businesses/","/how-it-works/","/facility/","/materials/","/community/","/people/","/where/","/contact/","/thanks/"]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); fails=[]
        for w,h,tag in [(1440,900,"d"),(390,844,"m")]:
            for path in PAGES:
                pg=await b.new_page(viewport={"width":w,"height":h}); errs=[]
                pg.on("console",lambda m: errs.append(m.text) if m.type=="error" else None)
                pg.on("response",lambda r: errs.append(f"{r.status} {r.url}") if r.status>=400 else None)
                await pg.goto("http://localhost:8090"+path); await pg.wait_for_timeout(300)
                await pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
                H=await pg.evaluate("document.documentElement.scrollHeight")
                for y in range(0,H,700): await pg.evaluate(f"window.scrollTo(0,{y})"); await pg.wait_for_timeout(40)
                await pg.evaluate("window.scrollTo(0,0)"); await pg.wait_for_timeout(300)
                await pg.evaluate("document.querySelectorAll('.fx').forEach(e=>e.classList.add('in'))")
                sw=await pg.evaluate("document.documentElement.scrollWidth")
                broken=await pg.evaluate("[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)")
                ov=await pg.evaluate("[...document.querySelectorAll('h1,h2,h3')].filter(e=>e.scrollWidth>e.clientWidth+2).map(e=>e.textContent.trim().slice(0,40))")
                name=path.strip('/').replace('/','-') or 'home'
                await pg.screenshot(path=f"shots/{tag}-{name}.png",full_page=True)
                status="OK" if (sw<=w and not errs and not broken and not ov) else "FAIL"
                if status=="FAIL": fails.append((tag,path,sw,errs,broken,ov))
                print(f"{tag} {path:16s} {status} h={H} sw={sw}")
                await pg.close()
        await b.close()
    for f in fails: print("FAIL",f)
asyncio.run(main())
