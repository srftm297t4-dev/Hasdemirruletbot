import os, asyncio, json, logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from provider import fetch_last_n_results
from strategy import basic_stats, suggestion

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '900'))  # 15 dk
MAX_RESULTS = int(os.getenv('MAX_RESULTS', '50'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STATE = {'spins': [], 'stats': None, 'suggestion': None}

def get_primary_prediction(sug):
    picks = (sug or {}).get('picks', [])
    for p in picks:
        if p['type'] == 'number': return p['value'], 'number'
    for p in picks:
        if p['type'] == 'color': return p['value'], 'color'
    return None, None

async def update_state_once():
    try:
        spins = await fetch_last_n_results(MAX_RESULTS)
        if not spins: return False
        STATE['spins'] = spins
        STATE['stats'] = basic_stats(spins)
        STATE['suggestion'] = suggestion(STATE['stats'])
        return True
    except Exception:
        logger.exception('update_state_once error')
        return False

async def poll_loop():
    while True:
        await update_state_once()
        await asyncio.sleep(POLL_INTERVAL)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not STATE['suggestion']:
        ok = await update_state_once()
        if not ok:
            await update.message.reply_text('Veri alınamadı, birazdan tekrar dene.')
            return
    val, typ = get_primary_prediction(STATE['suggestion'])
    if not val:
        hot = (STATE['stats'] or {}).get('hot_nums', [])
        if hot: val, typ = hot[0][0], 'number'
    if not val:
        await update.message.reply_text('Şu an tahmin üretemedim.')
        return
    if typ == 'number':
        await update.message.reply_text(f'🔮 Tahminim: **{val}** (sayı)', parse_mode='Markdown')
    else:
        await update.message.reply_text(f'🔮 Tahminim: **{val}** (renk)', parse_mode='Markdown')

async def once_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await update_state_once():
        await update.message.reply_text('✅ Analiz güncellendi. /start ile tahmini al.')

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(json.dumps({
        'count': (STATE['stats'] or {}).get('count'),
        'hot_nums': (STATE['stats'] or {}).get('hot_nums'),
        'color_counts': (STATE['stats'] or {}).get('color_counts'),
    }, ensure_ascii=False, indent=2))

def main():
    if not BOT_TOKEN:
        raise SystemExit('BOT_TOKEN eksik.')
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start_cmd))
    app.add_handler(CommandHandler('once', once_cmd))
    app.add_handler(CommandHandler('status', status_cmd))

    async def _startup(app):
        asyncio.create_task(poll_loop())  # 15 dk’da bir güncelle
    app.post_init = _startup

    app.run_polling()

if __name__ == '__main__':
    main()
