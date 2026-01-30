import asyncio
from playwright.async_api import async_playwright
import os

async def verify():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda exc: print(f"PAGE ERROR: {exc}"))
        page.on("requestfailed", lambda request: print(f"REQUEST FAILED: {request.url}"))

        file_path = "file://" + os.path.abspath("index.html")
        await page.goto(file_path)

        print("Pagina caricata. Inizio simulazione analisi...")

        await page.wait_for_selector('input[type="file"]', state="attached")

        await page.evaluate("""
            const input = document.querySelector('input[type="file"]');
            const dataTransfer = new DataTransfer();
            const file = new File([''], 'test.png', { type: 'image/png' });
            dataTransfer.items.add(file);
            input.files = dataTransfer.files;
            input.dispatchEvent(new Event('change', { bubbles: true }));
        """)

        # Aspetta che appaia il pulsante "Analizza Landing Page"
        await page.wait_for_selector('button:has-text("Analizza Landing Page")')
        await page.click('button:has-text("Analizza Landing Page")')

        print("Analisi avviata. Attesa completamento (4s + buffer)...")
        # Il mock dura 4 secondi
        await page.wait_for_selector('h2:has-text("Audit Avanzato CRO")', timeout=15000)

        print("Report generato. Verifico sezioni...")

        # Verifica Executive Summary (Point 0)
        await page.wait_for_selector('h2:has-text("0. Executive Summary")')

        # Verifica categorie (1-40)
        categories = [
            "Attenzione e Prima Impressione",
            "Messaggio e Promessa",
            "Persuasione e Fiducia",
            "Azione e Frizione",
            "Percorso Decisionale",
            "Chiarezza dell'Offerta",
            "Target e Coerenza del Messaggio",
            "Focus sulla Conversione",
            "Struttura e Profondità"
        ]
        for cat in categories:
            if await page.query_selector(f'h2:has-text("{cat}")'):
                print(f"Categoria '{cat}' trovata.")
            else:
                print(f"ERRORE: Categoria '{cat}' NON trovata.")

        # Verifica punti specifici (es. #40)
        if await page.query_selector('div:has-text("#40")'):
            print("Punto #40 trovato.")
        else:
            print("ERRORE: Punto #40 NON trovato.")

        # Verifica Ottimizzazione (41-44)
        await page.wait_for_selector('h3:has-text("41. Stima Impatto sulle Conversioni")')
        await page.wait_for_selector('h3:has-text("42. 5 Azioni ad Alto Impatto")')
        await page.wait_for_selector('h3:has-text("43. Piano di Test A/B")')

        # Verifica Riepilogo Finale (45)
        await page.wait_for_selector('h2:has-text("45. Riepilogo Finale")')

        # Screenshot per conferma visiva
        await page.screenshot(path="screenshot_45_points.png", full_page=True)
        print("Screenshot salvato: screenshot_45_points.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify())
