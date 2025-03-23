import itertools
import flet as ft
from board_list import BoardList
from data_store import DataStore


class Board(ft.Container):
    id_counter = itertools.count()

    def __init__(self, app, store: DataStore, name: str, page: ft.Page):
        self.page: ft.Page = page
        self.board_id = next(Board.id_counter)
        self.store: DataStore = store
        self.app = app
        self.name = name
        self.add_list_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD, text="add a list", height=30, on_click=self.create_list
        )
        
        self.filter_button = ft.TextButton(
            "Tags",
            icon=ft.Icons.LABEL,
            icon_color=ft.Colors.BLUE,
            on_click=self.show_tags_popup,
            style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.BLUE_200,
                ft.ControlState.HOVERED: ft.Colors.BLUE_400,
            },
            shape={
                ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=3)
            },
            color={
                ft.ControlState.DEFAULT: ft.Colors.BLACK,
            },
            ),
        )

        self.board_lists = ft.Row(
            controls=[self.add_list_button],
            vertical_alignment=ft.CrossAxisAlignment.START,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            width=(self.app.page.width - 310),
            height=(self.app.page.height - 95),
        )
        for l in self.store.get_lists_by_board(self.board_id):
            self.add_list(l)

        super().__init__(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(value=self.name, style=ft.TextTheme.headline_medium),
                            self.filter_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    self.board_lists,
                ],
                spacing=10,
            ),
            data=self,
            margin=ft.margin.all(0),
            padding=ft.padding.only(top=10, right=0),
            height=self.app.page.height,
        )

    def resize(self, nav_rail_extended, width, height):
        self.board_lists.width = (width - 310) if nav_rail_extended else (width - 50)
        self.height = height
        self.update()

    def create_list(self, e):

        option_dict = {
            ft.Colors.LIGHT_GREEN: self.color_option_creator(ft.Colors.LIGHT_GREEN),
            ft.Colors.RED_200: self.color_option_creator(ft.Colors.RED_200),
            ft.Colors.AMBER_500: self.color_option_creator(ft.Colors.AMBER_500),
            ft.Colors.PINK_300: self.color_option_creator(ft.Colors.PINK_300),
            ft.Colors.ORANGE_300: self.color_option_creator(ft.Colors.ORANGE_300),
            ft.Colors.LIGHT_BLUE: self.color_option_creator(ft.Colors.LIGHT_BLUE),
            ft.Colors.DEEP_ORANGE_300: self.color_option_creator(
                ft.Colors.DEEP_ORANGE_300
            ),
            ft.Colors.PURPLE_100: self.color_option_creator(ft.Colors.PURPLE_100),
            ft.Colors.RED_700: self.color_option_creator(ft.Colors.RED_700),
            ft.Colors.TEAL_500: self.color_option_creator(ft.Colors.TEAL_500),
            ft.Colors.YELLOW_400: self.color_option_creator(ft.Colors.YELLOW_400),
            ft.Colors.PURPLE_400: self.color_option_creator(ft.Colors.PURPLE_400),
            ft.Colors.BROWN_300: self.color_option_creator(ft.Colors.BROWN_300),
            ft.Colors.CYAN_500: self.color_option_creator(ft.Colors.CYAN_500),
            ft.Colors.BLUE_GREY_500: self.color_option_creator(ft.Colors.BLUE_GREY_500),
        }

        def set_color(e):
            color_options.data = e.control.data
            for k, v in option_dict.items():
                if k == e.control.data:
                    v.border = ft.border.all(3, ft.Colors.BLACK26)
                else:
                    v.border = None
            dialog.content.update()

        color_options = ft.GridView(runs_count=3, max_extent=40, data="", height=150)

        for _, v in option_dict.items():
            v.on_click = set_color
            color_options.controls.append(v)

        def close_dlg(e):
            if (hasattr(e.control, "text") and not e.control.text == "Cancel") or (
                type(e.control) is ft.TextField and e.control.value != ""
            ):
                new_list = BoardList(
                    self,
                    self.store,
                    dialog_text.value,
                    self.page,
                    color=color_options.data,
                )
                self.add_list(new_list)
            self.page.close(dialog)

        def textfield_change(e):
            if dialog_text.value == "":
                create_button.disabled = True
            else:
                create_button.disabled = False
            self.page.update()

        dialog_text = ft.TextField(
            label="New List Name", on_submit=close_dlg, on_change=textfield_change
        )
        create_button = ft.ElevatedButton(
            text="Create", bgcolor=ft.Colors.BLUE_200, on_click=close_dlg, disabled=True
        )
        dialog = ft.AlertDialog(
            title=ft.Text("Name your new list"),
            content=ft.Column(
                [
                    ft.Container(
                        content=dialog_text, padding=ft.padding.symmetric(horizontal=5)
                    ),
                    color_options,
                    ft.Row(
                        [
                            ft.ElevatedButton(text="Cancel", on_click=close_dlg),
                            create_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
        self.page.open(dialog)
        dialog_text.focus()

    def remove_list(self, list: BoardList, e):
        self.board_lists.controls.remove(list)
        self.store.remove_list(self.board_id, list.board_list_id)
        self.page.update()

    def add_list(self, list):
        self.board_lists.controls.insert(-1, list)
        self.store.add_list(self.board_id, list)
        self.page.update()

    def color_option_creator(self, color: str):
        return ft.Container(
            bgcolor=color,
            border_radius=ft.border_radius.all(50),
            height=10,
            width=10,
            padding=ft.padding.all(5),
            alignment=ft.alignment.center,
            data=color,
        )

    def show_tags_popup(self, e):
        labels = self.get_all_labels()
        checkboxes = [ft.Checkbox(label=label, on_change=self.filter_by_label) for label in labels]

        dialog = ft.AlertDialog(
            title=ft.Text("Filter by Tags"),
            content=ft.Column(checkboxes, tight=True),
        )
        self.page.open(dialog)

    def get_all_labels(self):
        labels = set()
        for board_list in self.store.get_lists_by_board(self.board_id):
            for item in self.store.get_items(board_list.board_list_id):
                labels.update(item.labels)
        return list(labels)

    def filter_by_label(self, e):
        selected_labels = [checkbox.label for checkbox in e.control.parent.controls if checkbox.value]
        for board_list in self.store.get_lists_by_board(self.board_id):
            for item in self.store.get_items(board_list.board_list_id):
                item.view.visible = (
                    True if not selected_labels else any(label in item.labels for label in selected_labels)
                )
        self.page.update()