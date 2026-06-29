import flet as ft
from db.local_db import get_history


class HistoryPage(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.bgcolor = "#0a0a14"
        self.padding = 20

        # Chart metric selector
        self.selected_metric = "ph_feed"
        self.metric_options = [
            ("pH Feed",        "ph_feed"),
            ("TDS Feed",       "tds_feed"),
            ("Pressure",       "pressure_feed"),
            ("Turbidity",      "turbidity_feed"),
            ("Temperature",    "temperature_feed"),
            ("Flow Rate",      "flow_rate_feed"),
        ]

        # Dropdown to pick metric
        self.metric_dropdown = ft.Dropdown(
            value="ph_feed",
            options=[ft.dropdown.Option(key=k, text=lbl) for lbl, k in self.metric_options],
            on_change=self._on_metric_change,
            bgcolor="#12121f",
            border_color="#00d2fc",
            color=ft.colors.WHITE,
            expand=True,
        )

        # Chart
        self.chart = ft.LineChart(
            data_series=[],
            border=ft.border.all(1, ft.colors.with_opacity(0.2, ft.colors.WHITE)),
            left_axis=ft.ChartAxis(labels_size=40),
            bottom_axis=ft.ChartAxis(labels_size=32),
            tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
            min_y=0,
            max_y=14,
            expand=True,
        )

        # Readings list (scrollable table rows)
        self.readings_list = ft.ListView(
            expand=True,
            spacing=6,
            item_extent=52,
        )

        self._data = []  # cached history rows

        self.content = ft.Column(
            [
                # Header
                ft.Text("Sensor History", size=22, weight=ft.FontWeight.BOLD, color="#00d2fc"),
                ft.Text("Locally stored readings (SQLite)", color=ft.colors.GREY_400, size=12),
                ft.Container(height=12),

                # Metric picker + chart
                ft.Row([
                    ft.Text("Metric:", color=ft.colors.GREY_300, size=13),
                    self.metric_dropdown,
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(
                    content=self.chart,
                    height=240,
                    padding=ft.padding.symmetric(horizontal=8, vertical=12),
                    bgcolor="#12121f",
                    border_radius=14,
                ),
                ft.Container(height=14),

                # Readings table header
                ft.Container(
                    content=ft.Row([
                        ft.Text("Time",        size=11, color=ft.colors.GREY_500, expand=3),
                        ft.Text("pH",          size=11, color=ft.colors.GREY_500, expand=2, text_align=ft.TextAlign.RIGHT),
                        ft.Text("TDS (ppm)",   size=11, color=ft.colors.GREY_500, expand=3, text_align=ft.TextAlign.RIGHT),
                        ft.Text("Temp (°C)",   size=11, color=ft.colors.GREY_500, expand=3, text_align=ft.TextAlign.RIGHT),
                        ft.Text("Press (bar)", size=11, color=ft.colors.GREY_500, expand=3, text_align=ft.TextAlign.RIGHT),
                    ]),
                    bgcolor="#12121f",
                    border_radius=ft.border_radius.only(top_left=10, top_right=10),
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                ),
                # Readings list
                ft.Container(
                    content=self.readings_list,
                    expand=True,
                    bgcolor="#0e0e1c",
                    border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                ),
            ],
            expand=True,
            spacing=4,
        )

    # ─────────────────────────────────────────────
    def _on_metric_change(self, e):
        self.selected_metric = e.control.value
        self._refresh_chart()
        self.chart.update()

    # ─────────────────────────────────────────────
    def _metric_y_range(self, metric):
        ranges = {
            "ph_feed":          (0,   14),
            "tds_feed":         (0,  600),
            "pressure_feed":    (0,   10),
            "turbidity_feed":   (0,   10),
            "temperature_feed": (0,   50),
            "flow_rate_feed":   (0,   25),
        }
        return ranges.get(metric, (0, 100))

    # ─────────────────────────────────────────────
    def _refresh_chart(self):
        """Re-draw the chart for the currently selected metric."""
        metric = self.selected_metric
        min_y, max_y = self._metric_y_range(metric)
        self.chart.min_y = min_y
        self.chart.max_y = max_y

        points = []
        for i, row in enumerate(self._data):
            val = row.get(metric)
            if val is not None:
                try:
                    points.append(ft.LineChartDataPoint(i, float(val)))
                except (ValueError, TypeError):
                    pass

        if points:
            ds = ft.LineChartData(
                data_points=points,
                stroke_width=2.5,
                color=ft.colors.CYAN,
                curved=True,
                stroke_cap_round=True,
                below_line_bgcolor=ft.colors.with_opacity(0.08, ft.colors.CYAN),
            )
            self.chart.data_series = [ds]
        else:
            self.chart.data_series = []

    # ─────────────────────────────────────────────
    def _refresh_list(self):
        """Rebuild the scrollable readings list."""
        self.readings_list.controls.clear()

        for i, row in enumerate(reversed(self._data)):   # newest first
            ts_raw = row.get("timestamp", "")
            # Trim to HH:MM:SS portion if ISO format
            if "T" in ts_raw:
                ts_display = ts_raw.split("T")[1][:8]
            else:
                ts_display = ts_raw[-8:] if len(ts_raw) >= 8 else ts_raw

            ph    = row.get("ph_feed",          "—")
            tds   = row.get("tds_feed",         "—")
            temp  = row.get("temperature_feed", "—")
            press = row.get("pressure_feed",    "—")

            def _fmt(v, decimals=1):
                try:
                    return f"{float(v):.{decimals}f}"
                except (TypeError, ValueError):
                    return "—"

            bg = "#12121f" if i % 2 == 0 else "#0f0f1a"

            self.readings_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Text(ts_display,   size=11, color=ft.colors.GREY_300, expand=3),
                        ft.Text(_fmt(ph),     size=11, color=ft.colors.CYAN,     expand=2, text_align=ft.TextAlign.RIGHT),
                        ft.Text(_fmt(tds, 0), size=11, color=ft.colors.TEAL_200, expand=3, text_align=ft.TextAlign.RIGHT),
                        ft.Text(_fmt(temp),   size=11, color=ft.colors.ORANGE_200, expand=3, text_align=ft.TextAlign.RIGHT),
                        ft.Text(_fmt(press),  size=11, color=ft.colors.PURPLE_200, expand=3, text_align=ft.TextAlign.RIGHT),
                    ]),
                    bgcolor=bg,
                    border_radius=6,
                    padding=ft.padding.symmetric(horizontal=6, vertical=8),
                )
            )

        if not self._data:
            self.readings_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.HOURGLASS_EMPTY, color=ft.colors.GREY_600, size=40),
                        ft.Text("No history yet.\nConnect to the sensor to start collecting data.",
                                color=ft.colors.GREY_500, text_align=ft.TextAlign.CENTER, size=13),
                    ], alignment=ft.MainAxisAlignment.CENTER,
                       horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=40,
                    alignment=ft.alignment.center,
                )
            )

    # ─────────────────────────────────────────────
    def update_data(self):
        """Fetch fresh data from SQLite and refresh chart + list."""
        self._data = get_history(limit=50)
        self._refresh_chart()
        self._refresh_list()

        # Only call .update() when the widget is already mounted on the page
        try:
            self.update()
        except Exception:
            pass
