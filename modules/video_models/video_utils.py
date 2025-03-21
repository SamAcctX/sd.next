import os
import time
from modules import shared, sd_models, timer


debug = shared.log.trace if os.environ.get('SD_VIDEO_DEBUG', None) is not None else lambda *args, **kwargs: None


def queue_err(msg):
    shared.log.error(f'Video: {msg}')
    return [], None, '', '', f'Error: {msg}'


def get_quant(args):
    if args is not None and "quantization_config" in args:
        return args['quantization_config'].__class__.__name__
    return None


def get_url(url):
    return f'&nbsp <a href="{url}" target="_blank" rel="noopener noreferrer" style="color: var(--button-primary-background-fill); font-weight: normal">{url}</a><br><br>' if url else '<br><br>'


def set_prompt(p):
    p.prompt = shared.prompt_styles.apply_styles_to_prompt(p.prompt, p.styles)
    p.negative_prompt = shared.prompt_styles.apply_negative_styles_to_prompt(p.negative_prompt, p.styles)
    p.task_args['prompt'] = p.prompt
    p.task_args['negative_prompt'] = p.negative_prompt


def hijack_encode_prompt(*args, **kwargs):
    t0 = time.time()
    res = shared.sd_model.orig_encode_prompt(*args, **kwargs)
    t1 = time.time()
    timer.process.add('te', t1-t0)
    debug(f'Video encode: te={shared.sd_model.text_encoder.__class__.__name__} time={t1-t0:.2f}')
    shared.sd_model = sd_models.apply_balanced_offload(shared.sd_model)
    return res
