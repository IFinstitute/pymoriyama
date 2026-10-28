import inspect
import os

import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

path_settings = [
    path_effects.Stroke(linewidth=5, foreground="white"),
    path_effects.Normal(),
]

def add_color_axis(ax, loc="right", size="3%", pad=0.1, axes_class=Axes):
    divider = make_axes_locatable(ax)
    cax = divider.append_axes(loc, size=size, pad=pad, axes_class=axes_class)
    return cax

def add_subplot_labels(
    fig, axes, labels=None, dx=0.01, dy=-0.01, loc='upper left', **kwargs
):
    """
    fig : Figure
    axes : list of Axes
    labels : list of str, optional
    dx, dy : float, オフセット（fig座標系、デフォルトは左上から少し右下）
    loc : str, 'upper left', 'lower left', 'upper right', 'lower right'
    kwargs : fig.textに渡す引数
    """
    if labels is None:
        labels = ['({})'.format(chr(97 + i)) for i in range(len(axes))]

    for ax, label in zip(axes, labels):
        bbox = ax.get_position()
        if loc == 'upper left':
            xpos = bbox.x0 + dx
            ypos = bbox.y1 + dy
            ha = 'left'
            va = 'top'
        elif loc == 'upper right':
            xpos = bbox.x1 + dx
            ypos = bbox.y1 + dy
            ha = 'right'
            va = 'top'
        elif loc == 'lower left':
            xpos = bbox.x0 + dx
            ypos = bbox.y0 + dy
            ha = 'left'
            va = 'bottom'
        elif loc == 'lower right':
            xpos = bbox.x1 + dx
            ypos = bbox.y0 + dy
            ha = 'right'
            va = 'bottom'
        else:
            raise ValueError("loc must be 'upper left', 'upper right', 'lower left', or 'lower right'.")

        fig.text(xpos, ypos, label, ha=ha, va=va, **kwargs).set_path_effects(path_settings)


def save_plot_image(suffix=""):
    # base_name, file_ext = os.path.splitext(os.path.basename(__file__))
    # parent_dir = os.path.basename(os.path.dirname(__file__))
    # In save_plot_image function, replace the line with:

    frame = inspect.currentframe()
    if frame is None:
        return
    caller = frame.f_back  # 安全にアクセス
    if caller is None:
    # 呼び出し元が取れない場合は安全に抜ける（必要なら例外に変更）
        del frame
        return
    filename = caller.f_code.co_filename

    base_name, _file_ext = os.path.splitext(os.path.basename(filename))
    parent_dir = os.path.dirname(filename)
    save_dir = os.path.join(
        parent_dir, "img", base_name
    )
    os.makedirs(save_dir, exist_ok=True)
    img_name = os.path.join(save_dir, base_name + f"_{suffix}.png")
    plt.savefig(img_name, bbox_inches="tight")
    print(f"saved {img_name} ..")
    plt.close()
