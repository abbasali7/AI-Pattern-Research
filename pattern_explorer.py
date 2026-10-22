# ============================================================
# OUR AI — SELECTABLE-RESOLUTION PATTERN EXPLORER
#
# CORRECTED VERSION
#
# FEATURES:
#   1. Width and height can be selected independently.
#   2. Exhaustive analysis for resolutions up to 16 pixels.
#   3. Three sliders: Branch, Original Member, Unique Pattern.
#   4. Pattern identity ignores translation, rotation and reflection.
#   5. Original-image and canonical-pattern pixel counts are separate.
#   6. Stronger branch and signature consistency checks.
#   7. Scrollable main content and fixed navigation footer.
#   8. Independently scrollable unique-pattern gallery.
#
# REQUIREMENTS:
#   Python 3
#   Tkinter
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from math import comb

MAX_PIXELS = 16


# ============================================================
# STEP 1 — GENERATE A MEMBER
# ============================================================

def make_member(n, p, m):
    """Generate member m containing exactly p white pixels."""
    if not 0 <= p <= n:
        raise ValueError("Invalid branch.")

    if not 0 <= m < comb(n, p):
        raise ValueError("Invalid member ID.")

    bits = []
    remaining_white = p
    rank = m

    for position in range(n):
        remaining_positions = n - position

        if remaining_white == 0:
            bits.extend([0] * remaining_positions)
            break

        if remaining_white == remaining_positions:
            bits.extend([1] * remaining_positions)
            break

        zero_completions = comb(
            remaining_positions - 1,
            remaining_white
        )

        if rank < zero_completions:
            bits.append(0)
        else:
            bits.append(1)
            rank -= zero_completions
            remaining_white -= 1

    if len(bits) != n or sum(bits) != p:
        raise AssertionError("Member generation check failed.")

    return bits


# ============================================================
# STEP 2 — BITS TO MATRIX
# ============================================================

def make_matrix(bits, width, height):
    if width * height != len(bits):
        raise ValueError("Matrix dimensions do not match bit count.")

    return [
        bits[y * width:(y + 1) * width]
        for y in range(height)
    ]


# ============================================================
# STEP 3 — NORMALIZE COORDINATES
# ============================================================

def normalize_positions(positions):
    """Remove absolute translation by moving the minimum x/y to zero."""
    if not positions:
        return ()

    min_y = min(y for y, x in positions)
    min_x = min(x for y, x in positions)

    return tuple(sorted(
        (y - min_y, x - min_x)
        for y, x in positions
    ))


# ============================================================
# STEP 4 — ROTATION
# ============================================================

def rotate_positions(positions):
    """Rotate coordinates by 90 degrees and normalize."""
    return normalize_positions([
        (x, -y)
        for y, x in positions
    ])


# ============================================================
# STEP 5 — REFLECTION
# ============================================================

def reflect_positions(positions):
    """Reflect coordinates and normalize."""
    return normalize_positions([
        (y, -x)
        for y, x in positions
    ])


# ============================================================
# STEP 6 — CANONICAL PATTERN SIGNATURE
# ============================================================

def get_pattern_signature(bits, width, height):
    """
    Translation, rotation and reflection are ignored.

    Generate all eight square symmetries and choose the
    lexicographically smallest normalized coordinate set.
    """
    matrix = make_matrix(bits, width, height)

    positions = [
        (y, x)
        for y in range(height)
        for x in range(width)
        if matrix[y][x] == 1
    ]

    original = normalize_positions(positions)
    reflected = reflect_positions(original)

    transformations = []

    for starting_shape in (original, reflected):
        current = starting_shape

        for _ in range(4):
            transformations.append(current)
            current = rotate_positions(current)

    return min(transformations)


# ============================================================
# STEP 7 — CANONICAL PATTERN DIMENSIONS
# ============================================================

def signature_dimensions(signature):
    """Return the smallest bounding-box dimensions."""
    if not signature:
        return 1, 1

    height = max(y for y, x in signature) + 1
    width = max(x for y, x in signature) + 1

    return width, height


# ============================================================
# STEP 8 — SIGNATURE TO MATRIX
# ============================================================

def signature_to_matrix(signature, width=None, height=None):
    """Render the complete canonical pattern without clipping."""
    if width is None or height is None:
        width, height = signature_dimensions(signature)

    if width < 1 or height < 1:
        raise ValueError("Matrix dimensions must be positive.")

    matrix = [
        [0] * width
        for _ in range(height)
    ]

    for y, x in signature:
        if not (0 <= y < height and 0 <= x < width):
            raise ValueError("Pattern does not fit matrix dimensions.")

        matrix[y][x] = 1

    return matrix


# ============================================================
# STEP 9 — EXHAUSTIVE ANALYSIS
# ============================================================

def analyze_all_branches(width, height):
    """Classify every binary image at the selected resolution."""
    if (
        width < 1
        or height < 1
        or width * height > MAX_PIXELS
    ):
        raise ValueError(
            f"Resolution must contain 1 to {MAX_PIXELS} pixels."
        )

    n = width * height
    results = {}
    total_unique_patterns = 0
    total_members_seen = 0

    for p in range(n + 1):
        branch_size = comb(n, p)

        signature_to_id = {}
        pattern_counts = {}
        member_pattern_ids = []
        pattern_signatures = {}
        pattern_first_members = {}

        for m in range(branch_size):
            bits = make_member(n, p, m)

            signature = get_pattern_signature(
                bits, width, height
            )

            if signature not in signature_to_id:
                pattern_id = len(signature_to_id) + 1

                signature_to_id[signature] = pattern_id
                pattern_counts[pattern_id] = 0
                pattern_signatures[pattern_id] = signature
                pattern_first_members[pattern_id] = m

            pattern_id = signature_to_id[signature]

            pattern_counts[pattern_id] += 1
            member_pattern_ids.append(pattern_id)

        branch_pattern_count = len(signature_to_id)

        # Branch-level mathematical consistency checks.
        if len(member_pattern_ids) != branch_size:
            raise AssertionError(
                f"Member coverage failed in branch p={p}."
            )

        if sum(pattern_counts.values()) != branch_size:
            raise AssertionError(
                f"Pattern multiplicities failed in branch p={p}."
            )

        if len(set(pattern_signatures.values())) != branch_pattern_count:
            raise AssertionError(
                f"Duplicate canonical signatures in branch p={p}."
            )

        total_unique_patterns += branch_pattern_count
        total_members_seen += branch_size

        results[p] = {
            "branch_size": branch_size,
            "pattern_count": branch_pattern_count,
            "pattern_counts": pattern_counts,
            "member_pattern_ids": member_pattern_ids,
            "pattern_signatures": pattern_signatures,
            "pattern_first_members": pattern_first_members,
        }

    if total_members_seen != 2 ** n:
        raise AssertionError("Total image coverage check failed.")

    return {
        "width": width,
        "height": height,
        "n": n,
        "total_images": 2 ** n,
        "total_branches": n + 1,
        "total_unique_patterns": total_unique_patterns,
        "branches": results,
    }


# ============================================================
# STEP 10 — MAIN APPLICATION
# ============================================================

class BranchExplorer:

    def __init__(self, root):
        self.root = root

        self.width = 4
        self.height = 4
        self.n = 16

        self.p = 2
        self.m = 0
        self.u = 1

        self.updating = False
        self.view_mode = "member"

        self.gallery_branch = None
        self.gallery_resolution = None

        self.analysis = None
        self.branch_data = None

        root.title("OUR AI — Unique Pattern Explorer")
        root.resizable(True, True)

        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()

        window_w = min(1180, screen_w)
        window_h = max(450, min(900, screen_h - 80))

        root.geometry(f"{window_w}x{window_h}+0+0")

        self.build_ui()
        self.recalculate_resolution()

    # ========================================================
    # STEP 11 — BUILD RESPONSIVE WINDOW
    # ========================================================

    def build_ui(self):
        outer = ttk.Frame(self.root)
        outer.pack(fill="both", expand=True)

        # Fixed navigation footer.
        self.footer = ttk.Frame(outer, padding=(6, 5))
        self.footer.pack(side="bottom", fill="x")

        ttk.Separator(
            outer, orient="horizontal"
        ).pack(side="bottom", fill="x")

        # Scrollable main content.
        scroll_area = ttk.Frame(outer)
        scroll_area.pack(side="top", fill="both", expand=True)

        self.content_canvas = tk.Canvas(
            scroll_area,
            highlightthickness=0,
            borderwidth=0
        )

        self.content_scrollbar = ttk.Scrollbar(
            scroll_area,
            orient="vertical",
            command=self.content_canvas.yview
        )

        self.content_canvas.configure(
            yscrollcommand=self.content_scrollbar.set
        )

        self.content_scrollbar.pack(side="right", fill="y")
        self.content_canvas.pack(side="left", fill="both", expand=True)

        self.main_frame = ttk.Frame(
            self.content_canvas,
            padding=8
        )

        self.content_window = self.content_canvas.create_window(
            (0, 0),
            window=self.main_frame,
            anchor="nw"
        )

        self.main_frame.bind(
            "<Configure>", self.on_content_configure
        )

        self.content_canvas.bind(
            "<Configure>", self.on_content_resize
        )

        self.content_canvas.bind(
            "<MouseWheel>", self.on_mousewheel
        )

        self.main_frame.bind(
            "<MouseWheel>", self.on_mousewheel
        )

        self.build_content()
        self.build_footer()

    # ========================================================
    # STEP 12 — MAIN SCROLL EVENTS
    # ========================================================

    def on_content_configure(self, event=None):
        self.content_canvas.configure(
            scrollregion=self.content_canvas.bbox("all")
        )

    def on_content_resize(self, event):
        self.content_canvas.itemconfigure(
            self.content_window,
            width=event.width
        )

    def on_mousewheel(self, event):
        self.content_canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )

    # ========================================================
    # STEP 13 — MAIN CONTENT
    # ========================================================

    def build_content(self):
        main = self.main_frame

        ttk.Label(
            main,
            text="OUR AI — IMAGE, MATRIX & UNIQUE PATTERNS",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 3))

        self.header_summary = ttk.Label(
            main,
            text="Calculating...",
            justify="center"
        )
        self.header_summary.pack(pady=(0, 7))

        # Resolution controls
        resolution_frame = ttk.LabelFrame(
            main,
            text="IMAGE RESOLUTION",
            padding=6
        )
        resolution_frame.pack(fill="x", pady=(0, 6))

        ttk.Label(
            resolution_frame, text="Width:"
        ).pack(side="left", padx=(2, 4))

        self.width_var = tk.StringVar(value="4")

        self.width_combo = ttk.Combobox(
            resolution_frame,
            textvariable=self.width_var,
            values=[str(i) for i in range(1, MAX_PIXELS + 1)],
            state="readonly",
            width=4
        )
        self.width_combo.pack(side="left", padx=(0, 10))

        ttk.Label(
            resolution_frame, text="Height:"
        ).pack(side="left", padx=(2, 4))

        self.height_var = tk.StringVar(value="4")

        self.height_combo = ttk.Combobox(
            resolution_frame,
            textvariable=self.height_var,
            values=[str(i) for i in range(1, MAX_PIXELS + 1)],
            state="readonly",
            width=4
        )
        self.height_combo.pack(side="left", padx=(0, 10))

        self.apply_resolution_button = ttk.Button(
            resolution_frame,
            text="Apply Resolution",
            command=self.recalculate_resolution
        )
        self.apply_resolution_button.pack(side="left", padx=4)

        ttk.Label(
            resolution_frame,
            text="Maximum: 16 total pixels"
        ).pack(side="left", padx=8)

        # Branch slider
        ttk.Label(
            main,
            text="SLIDER 1 — BRANCH (white-pixel count)",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.branch_label = ttk.Label(main, text="")
        self.branch_label.pack(anchor="w")

        self.branch_slider = tk.Scale(
            main,
            from_=0,
            to=self.n,
            orient="horizontal",
            resolution=1,
            command=self.branch_changed,
            highlightthickness=0,
            bd=0,
            sliderlength=18,
            showvalue=True,
            length=400
        )
        self.branch_slider.pack(fill="x", pady=(0, 3))

        # Member slider
        ttk.Label(
            main,
            text="SLIDER 2 — ORIGINAL MEMBER",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.member_label = ttk.Label(main, text="")
        self.member_label.pack(anchor="w")

        self.member_slider = tk.Scale(
            main,
            from_=0,
            to=1,
            orient="horizontal",
            resolution=1,
            command=self.member_changed,
            highlightthickness=0,
            bd=0,
            sliderlength=18,
            showvalue=True,
            length=400
        )
        self.member_slider.pack(fill="x", pady=(0, 3))

        # Unique-pattern slider
        ttk.Label(
            main,
            text="SLIDER 3 — UNIQUE PATTERN",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        self.pattern_label = ttk.Label(main, text="")
        self.pattern_label.pack(anchor="w")

        self.pattern_slider = tk.Scale(
            main,
            from_=1,
            to=1,
            orient="horizontal",
            resolution=1,
            command=self.pattern_changed,
            highlightthickness=0,
            bd=0,
            sliderlength=18,
            showvalue=True,
            length=400
        )
        self.pattern_slider.pack(fill="x", pady=(0, 5))

        # Image and matrix
        display = ttk.Frame(main)
        display.pack(fill="x", pady=4)

        self.image_frame = ttk.LabelFrame(
            display,
            text="IMAGE / CANONICAL PATTERN",
            padding=5
        )
        self.image_frame.pack(
            side="left", padx=(0, 5), anchor="n"
        )

        self.image_canvas = tk.Canvas(
            self.image_frame,
            width=120,
            height=120,
            bg="black",
            highlightthickness=0
        )
        self.image_canvas.pack()

        self.matrix_frame = ttk.LabelFrame(
            display,
            text="BINARY MATRIX",
            padding=5
        )
        self.matrix_frame.pack(
            side="left", padx=5, anchor="n"
        )

        self.matrix_canvas = tk.Canvas(
            self.matrix_frame,
            width=120,
            height=120,
            bg="white",
            highlightthickness=0
        )
        self.matrix_canvas.pack()

        self.matrix_text = ttk.Label(
            main,
            text="",
            font=("Consolas", 9),
            justify="left"
        )
        self.matrix_text.pack(anchor="w", pady=3)

        # Research results
        result_frame = ttk.LabelFrame(
            main,
            text="RESEARCH RESULTS",
            padding=6
        )
        result_frame.pack(fill="x", pady=4)

        self.result_label = ttk.Label(
            result_frame,
            text="",
            font=("Consolas", 9),
            justify="left"
        )
        self.result_label.pack(anchor="w")

        # Unique-pattern gallery
        gallery_frame = ttk.LabelFrame(
            main,
            text="UNIQUE PATTERNS IN THIS BRANCH",
            padding=6
        )
        gallery_frame.pack(
            fill="both", expand=True, pady=(5, 4)
        )

        ttk.Label(
            gallery_frame,
            text=(
                "Each tile represents one unique shape. "
                "Translations, rotations and reflections are grouped."
            ),
            wraplength=850
        ).pack(anchor="w", pady=(0, 4))

        gallery_body = ttk.Frame(gallery_frame)
        gallery_body.pack(fill="both", expand=True)

        self.gallery_canvas = tk.Canvas(
            gallery_body,
            height=180,
            highlightthickness=0
        )

        self.gallery_scrollbar = ttk.Scrollbar(
            gallery_body,
            orient="vertical",
            command=self.gallery_canvas.yview
        )

        self.gallery_canvas.configure(
            yscrollcommand=self.gallery_scrollbar.set
        )

        self.gallery_scrollbar.pack(side="right", fill="y")
        self.gallery_canvas.pack(side="left", fill="both", expand=True)

        self.gallery_inner = ttk.Frame(self.gallery_canvas)

        self.gallery_window = self.gallery_canvas.create_window(
            (0, 0),
            window=self.gallery_inner,
            anchor="nw"
        )

        self.gallery_inner.bind(
            "<Configure>", self.on_gallery_configure
        )

        self.gallery_canvas.bind(
            "<Configure>", self.on_gallery_resize
        )

        self.gallery_canvas.bind(
            "<MouseWheel>", self.on_gallery_mousewheel
        )

    # ========================================================
    # STEP 14 — FIXED FOOTER
    # ========================================================

    def build_footer(self):
        ttk.Button(
            self.footer,
            text="Previous Member",
            command=lambda: self.step_member(-1)
        ).pack(side="left", padx=3)

        ttk.Button(
            self.footer,
            text="Next Member",
            command=lambda: self.step_member(1)
        ).pack(side="left", padx=3)

        ttk.Button(
            self.footer,
            text="First Member",
            command=lambda: self.set_member(0)
        ).pack(side="left", padx=3)

        ttk.Button(
            self.footer,
            text="Last Member",
            command=self.last_member
        ).pack(side="left", padx=3)

        ttk.Button(
            self.footer,
            text="Top",
            command=lambda: self.content_canvas.yview_moveto(0)
        ).pack(side="right", padx=3)

    # ========================================================
    # STEP 15 — DRAW IMAGE AND MATRIX
    # ========================================================

    def draw_matrix(self, matrix):
        height = len(matrix)
        width = len(matrix[0]) if height else 1

        cell_size = max(
            12,
            min(36, 420 // max(width, height, 1))
        )

        canvas_width = width * cell_size
        canvas_height = height * cell_size

        for canvas in (self.image_canvas, self.matrix_canvas):
            canvas.delete("all")
            canvas.configure(
                width=canvas_width,
                height=canvas_height,
                scrollregion=(0, 0, canvas_width, canvas_height)
            )

        for y, row in enumerate(matrix):
            for x, value in enumerate(row):
                x1 = x * cell_size
                y1 = y * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                self.image_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="white" if value else "black",
                    outline="#777777",
                    width=1
                )

                self.matrix_canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#202020" if value else "white",
                    outline="#777777",
                    width=1
                )

                self.matrix_canvas.create_text(
                    x1 + cell_size / 2,
                    y1 + cell_size / 2,
                    text=str(value),
                    fill="white" if value else "black",
                    font=(
                        "Consolas",
                        max(7, min(14, cell_size // 2)),
                        "bold"
                    )
                )

        self.matrix_text.configure(
            text=(
                f"Matrix dimensions: {width} x {height}\n"
                + "\n".join(
                    " ".join(str(value) for value in row)
                    for row in matrix
                )
            )
        )

    # ========================================================
    # STEP 16 — APPLY RESOLUTION
    # ========================================================

    def recalculate_resolution(self):
        try:
            new_width = int(self.width_var.get())
            new_height = int(self.height_var.get())
        except (ValueError, tk.TclError):
            messagebox.showerror(
                "Invalid resolution",
                "Please select valid width and height values."
            )
            return

        new_n = new_width * new_height

        if (
            new_width < 1
            or new_height < 1
            or new_n > MAX_PIXELS
        ):
            messagebox.showerror(
                "Unsupported resolution",
                f"Width and height must be positive, and their product "
                f"cannot exceed {MAX_PIXELS}.\n\n"
                f"Selected: {new_width} x {new_height} = {new_n} pixels."
            )
            self.width_var.set(str(self.width))
            self.height_var.set(str(self.height))
            return

        self.apply_resolution_button.configure(state="disabled")
        self.root.configure(cursor="watch")
        self.root.update_idletasks()

        try:
            # Complete analysis before changing the current resolution.
            new_analysis = analyze_all_branches(
                new_width, new_height
            )

            self.width = new_width
            self.height = new_height
            self.n = new_n

            self.analysis = new_analysis
            self.branch_data = new_analysis["branches"]

            self.p = min(2, self.n)
            self.m = 0
            self.u = 1
            self.view_mode = "member"

            self.gallery_branch = None
            self.gallery_resolution = None

            self.updating = True
            try:
                self.branch_slider.configure(
                    from_=0, to=self.n
                )
                self.branch_slider.set(self.p)

                self.member_slider.configure(
                    from_=0,
                    to=self.branch_data[self.p]["branch_size"] - 1
                )
                self.member_slider.set(0)

                self.pattern_slider.configure(
                    from_=1,
                    to=self.branch_data[self.p]["pattern_count"]
                )
                self.pattern_slider.set(1)
            finally:
                self.updating = False

            self.update_header()
            self.update_image()

        except Exception as exc:
            messagebox.showerror(
                "Analysis error",
                f"Could not analyze this resolution:\n{exc}"
            )
            self.width_var.set(str(self.width))
            self.height_var.set(str(self.height))

        finally:
            self.root.configure(cursor="")
            self.apply_resolution_button.configure(state="normal")

    # ========================================================
    # STEP 17 — HEADER SUMMARY
    # ========================================================

    def update_header(self):
        a = self.analysis

        self.header_summary.configure(
            text=(
                f"Resolution: {self.width} x {self.height} = {self.n} pixels\n"
                f"{a['total_branches']:,} branches | "
                f"{a['total_images']:,} original images | "
                f"{a['total_unique_patterns']:,} TOTAL UNIQUE PATTERNS\n"
                "Identity: translation, 90-degree rotation, and reflection "
                "are equivalent"
            )
        )

    # ========================================================
    # STEP 18 — GALLERY SCROLL EVENTS
    # ========================================================

    def on_gallery_configure(self, event=None):
        self.gallery_canvas.configure(
            scrollregion=self.gallery_canvas.bbox("all")
        )

    def on_gallery_resize(self, event):
        self.gallery_canvas.itemconfigure(
            self.gallery_window,
            width=event.width
        )

    def on_gallery_mousewheel(self, event):
        self.gallery_canvas.yview_scroll(
            int(-event.delta / 120),
            "units"
        )

    # ========================================================
    # STEP 19 — UNIQUE PATTERN GALLERY
    # ========================================================

    def update_gallery(self):
        for widget in self.gallery_inner.winfo_children():
            widget.destroy()

        branch = self.branch_data[self.p]
        signatures = branch["pattern_signatures"]
        counts = branch["pattern_counts"]
        columns = 4

        for index, pattern_id in enumerate(signatures):
            signature = signatures[pattern_id]
            count = counts[pattern_id]

            shape_width, shape_height = signature_dimensions(
                signature
            )

            thumbnail_cell = max(
                6,
                min(
                    18,
                    112 // max(shape_width, shape_height, 1)
                )
            )

            tile = ttk.LabelFrame(
                self.gallery_inner,
                text=f"Pattern {pattern_id}",
                padding=4
            )

            tile.grid(
                row=index // columns,
                column=index % columns,
                padx=4,
                pady=4,
                sticky="n"
            )

            mini = tk.Canvas(
                tile,
                width=shape_width * thumbnail_cell,
                height=shape_height * thumbnail_cell,
                bg="black",
                highlightthickness=0
            )
            mini.pack()

            pattern_matrix = signature_to_matrix(signature)

            for y, row in enumerate(pattern_matrix):
                for x, value in enumerate(row):
                    mini.create_rectangle(
                        x * thumbnail_cell,
                        y * thumbnail_cell,
                        (x + 1) * thumbnail_cell,
                        (y + 1) * thumbnail_cell,
                        fill="white" if value else "black",
                        outline="#666666",
                        width=1
                    )

            ttk.Label(
                tile,
                text=(
                    f"Members: {count:,}\n"
                    f"Shape: {shape_width} x {shape_height}"
                ),
                font=("Segoe UI", 8)
            ).pack(pady=(3, 0))

        for col in range(columns):
            self.gallery_inner.grid_columnconfigure(
                col, weight=1
            )

        self.gallery_canvas.yview_moveto(0)
        self.on_gallery_configure()

    # ========================================================
    # STEP 20 — BRANCH SLIDER
    # ========================================================

    def branch_changed(self, value=None):
        if self.updating or self.branch_data is None:
            return

        self.p = int(float(value))
        branch = self.branch_data[self.p]

        self.updating = True
        try:
            self.m = 0
            self.u = 1
            self.view_mode = "member"

            self.member_slider.configure(
                to=branch["branch_size"] - 1
            )
            self.member_slider.set(0)

            self.pattern_slider.configure(
                to=branch["pattern_count"]
            )
            self.pattern_slider.set(1)
        finally:
            self.updating = False

        self.gallery_branch = None
        self.update_image()

    # ========================================================
    # STEP 21 — MEMBER SLIDER
    # ========================================================

    def member_changed(self, value=None):
        if self.updating or self.branch_data is None:
            return

        self.m = int(float(value))
        self.view_mode = "member"
        self.update_image()

    # ========================================================
    # STEP 22 — UNIQUE PATTERN SLIDER
    # ========================================================

    def pattern_changed(self, value=None):
        if self.updating or self.branch_data is None:
            return

        branch = self.branch_data[self.p]

        self.u = max(
            1,
            min(int(float(value)), branch["pattern_count"])
        )

        self.view_mode = "pattern"
        self.m = branch["pattern_first_members"][self.u]

        self.updating = True
        try:
            self.member_slider.set(self.m)
        finally:
            self.updating = False

        self.update_image()

    # ========================================================
    # STEP 23 — MEMBER NAVIGATION
    # ========================================================

    def set_member(self, member_id):
        branch_size = self.branch_data[self.p]["branch_size"]

        self.m = max(
            0,
            min(int(member_id), branch_size - 1)
        )

        self.view_mode = "member"

        self.updating = True
        try:
            self.member_slider.set(self.m)
        finally:
            self.updating = False

        self.update_image()

    def step_member(self, amount):
        self.set_member(self.m + amount)

    def last_member(self):
        self.set_member(
            self.branch_data[self.p]["branch_size"] - 1
        )

    # ========================================================
    # STEP 24 — UPDATE IMAGE, MATRIX AND RESULTS
    # ========================================================

    def update_image(self):
        p = self.p
        m = self.m

        branch = self.branch_data[p]
        branch_size = branch["branch_size"]
        pattern_count = branch["pattern_count"]

        member_bits = make_member(self.n, p, m)

        member_signature = get_pattern_signature(
            member_bits,
            self.width,
            self.height
        )

        member_pattern_id = branch["member_pattern_ids"][m]

        if self.view_mode == "member":
            self.u = member_pattern_id

        self.updating = True
        try:
            self.pattern_slider.set(self.u)
        finally:
            self.updating = False

        if self.view_mode == "pattern":
            displayed_pattern_id = self.u
            signature = branch["pattern_signatures"][
                displayed_pattern_id
            ]
            matrix = signature_to_matrix(signature)
            displayed_title = "CANONICAL UNIQUE PATTERN"
        else:
            displayed_pattern_id = member_pattern_id
            signature = branch["pattern_signatures"][
                displayed_pattern_id
            ]
            matrix = make_matrix(
                member_bits, self.width, self.height
            )
            displayed_title = "ORIGINAL MEMBER IMAGE"

        # Correct pixel statistics: canonical matrix dimensions can
        # differ from the dimensions of the original image.
        displayed_height = len(matrix)
        displayed_width = len(matrix[0]) if displayed_height else 0
        displayed_cells = displayed_width * displayed_height

        displayed_white_count = sum(
            sum(row) for row in matrix
        )
        displayed_black_count = displayed_cells - displayed_white_count

        original_white_count = sum(member_bits)
        original_black_count = self.n - original_white_count

        members_in_pattern = branch["pattern_counts"][
            displayed_pattern_id
        ]

        self.draw_matrix(matrix)

        self.branch_label.configure(
            text=(
                f"Branch p = {p} | "
                f"Members = C({self.n}, {p}) = {branch_size:,}"
            )
        )

        self.member_label.configure(
            text=(
                f"Member ID: {m} | "
                f"Valid IDs: 0 to {branch_size - 1:,}"
            )
        )

        self.pattern_label.configure(
            text=(
                f"Unique Pattern ID: {self.u} | "
                f"Valid IDs: 1 to {pattern_count:,}"
            )
        )

        # Stronger consistency checks.
        checks_passed = (
            len(member_bits) == self.n
            and original_white_count == p
            and len(branch["member_pattern_ids"]) == branch_size
            and sum(branch["pattern_counts"].values()) == branch_size
            and len(set(branch["pattern_signatures"].values()))
                == pattern_count
            and branch["pattern_signatures"][member_pattern_id]
                == member_signature
            and branch["pattern_signatures"][member_pattern_id]
                == branch["pattern_signatures"][displayed_pattern_id]
            and displayed_white_count == p
            and displayed_black_count == displayed_cells - p
        )

        mode_text = (
            "UNIQUE PATTERN VIEW"
            if self.view_mode == "pattern"
            else "ORIGINAL MEMBER VIEW"
        )

        self.result_label.configure(
            text=(
                f"Displayed:                  {displayed_title}\n"
                f"View mode:                  {mode_text}\n"
                f"Selected resolution:        {self.width} x {self.height}\n"
                f"Total pixels in original:   {self.n}\n"
                f"Original images:            "
                f"{self.analysis['total_images']:,}\n"
                f"Total branches:             "
                f"{self.analysis['total_branches']:,}\n"
                f"TOTAL unique patterns:      "
                f"{self.analysis['total_unique_patterns']:,}\n"
                f"Members in selected branch: {branch_size:,}\n"
                f"Unique patterns in branch:  {pattern_count:,}\n"
                f"Members beyond pattern count: "
                f"{branch_size - pattern_count:,}\n"
                f"Selected member ID:         {m}\n"
                f"Selected pattern ID:        {displayed_pattern_id}\n"
                f"Members with this pattern:  {members_in_pattern:,}\n"
                f"Original image white/black: "
                f"{original_white_count} / {original_black_count}\n"
                f"Displayed matrix size:      "
                f"{displayed_width} x {displayed_height} "
                f"= {displayed_cells} cells\n"
                f"Displayed matrix white/black: "
                f"{displayed_white_count} / {displayed_black_count}\n"
                f"Canonical signature:        "
                f"{branch['pattern_signatures'][displayed_pattern_id]}\n"
                f"Identity rule:               "
                f"translation + rotation + reflection\n"
                f"Basic checks:                "
                f"{'PASS' if checks_passed else 'FAIL'}"
            )
        )

        current_resolution = (self.width, self.height)

        if (
            self.gallery_branch != p
            or self.gallery_resolution != current_resolution
        ):
            self.gallery_branch = p
            self.gallery_resolution = current_resolution
            self.update_gallery()


# ============================================================
# STEP 25 — RUN APPLICATION
# ============================================================

def main():
    root = tk.Tk()

    try:
        style = ttk.Style(root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except tk.TclError:
        pass

    BranchExplorer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
