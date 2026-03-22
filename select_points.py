"""
Point correspondence selector.

Usage:
    python select_points.py [example]

Opens both images from pictures/<example>/ and lets you pick 4 corresponding
points by clicking alternately between them. Saves the result to
pictures/<example>/points.json, which the notebook reads from.
"""

import sys
import json
import os
import argparse

import matplotlib
_BACKENDS = [("TkAgg", "tkinter"), ("Qt5Agg", "PyQt5"), ("QtAgg", "PyQt6"), ("GTK3Agg", "gi")]
for _backend, _dep in _BACKENDS:
    try:
        __import__(_dep)
        matplotlib.use(_backend)
        break
    except ImportError:
        continue
else:
    print("No GUI backend found. Install tkinter, PyQt5, PyQt6, or gi.")
    sys.exit(1)

import matplotlib.pyplot as plt
import matplotlib.image as mpimg


N_POINTS = 4
COLORS = ["red", "lime", "blue", "orange"]


def main():
    parser = argparse.ArgumentParser(description="Pick corresponding points between two images.")
    parser.add_argument("example", nargs="?", default="ex_1",
                        help="Example folder name under pictures/ (default: ex_1)")
    args = parser.parse_args()

    img_dir = os.path.join("pictures", args.example)
    img_files = sorted(
        f for f in os.listdir(img_dir)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )

    if len(img_files) < 2:
        print(f"Error: need at least 2 images in {img_dir}")
        sys.exit(1)

    img_a = mpimg.imread(os.path.join(img_dir, img_files[0]))
    img_b = mpimg.imread(os.path.join(img_dir, img_files[1]))

    points_a = []
    points_b = []
    state = {"next": "a", "count": 0}

    fig, (ax_a, ax_b) = plt.subplots(2, 1, figsize=(10, 16))
    ax_a.imshow(img_a)
    ax_a.set_title(f"{img_files[0]} — click point 1", fontsize=13)
    ax_a.axis("off")
    ax_b.imshow(img_b)
    ax_b.set_title(img_files[1], fontsize=13)
    ax_b.axis("off")
    plt.tight_layout()

    def on_click(event):
        total = state["count"]
        if total >= N_POINTS * 2 or event.xdata is None:
            return

        pair_idx = total // 2

        if state["next"] == "a" and event.inaxes is ax_a:
            points_a.append([event.xdata, event.ydata])
            ax_a.plot(event.xdata, event.ydata, "o", color=COLORS[pair_idx], markersize=9)
            ax_a.text(event.xdata + 8, event.ydata - 8, str(pair_idx + 1),
                      color=COLORS[pair_idx], fontsize=12, fontweight="bold")
            state["next"] = "b"
            state["count"] += 1
            ax_a.set_title(f"{img_files[0]} — {pair_idx + 1}/{N_POINTS} done", fontsize=13)
            ax_b.set_title(f"{img_files[1]} — click point {pair_idx + 1}", fontsize=13)

        elif state["next"] == "b" and event.inaxes is ax_b:
            points_b.append([event.xdata, event.ydata])
            ax_b.plot(event.xdata, event.ydata, "o", color=COLORS[pair_idx], markersize=9)
            ax_b.text(event.xdata + 8, event.ydata - 8, str(pair_idx + 1),
                      color=COLORS[pair_idx], fontsize=12, fontweight="bold")
            state["count"] += 1
            if state["count"] < N_POINTS * 2:
                next_pair = state["count"] // 2
                state["next"] = "a"
                ax_a.set_title(f"{img_files[0]} — click point {next_pair + 1}", fontsize=13)
                ax_b.set_title(f"{img_files[1]} — {pair_idx + 1}/{N_POINTS} done", fontsize=13)
            else:
                ax_a.set_title(f"{img_files[0]} — done ✓", fontsize=13)
                ax_b.set_title(f"{img_files[1]} — done ✓", fontsize=13)
                out_path = os.path.join(img_dir, "points.json")
                with open(out_path, "w") as f:
                    json.dump({"images": img_files[:2],
                               "points_a": points_a,
                               "points_b": points_b}, f, indent=2)
                print(f"Saved {N_POINTS} correspondences to {out_path}")

        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_click)
    print(f"Click alternately: point 1 in A → point 1 in B → ... ({N_POINTS} pairs total)")
    plt.show()


if __name__ == "__main__":
    main()
