import flet as ft
from app_layout import AppLayout
from board import Board
from user import User
from data_store import DataStore
from memory_store import InMemoryStore
from user import User


class TrelloApp(AppLayout):
    def __init__(self, page: ft.Page, store: DataStore):
        self.page: ft.Page = page
        self.store: DataStore = store
        self.user: str | None = None
        self.page.on_route_change = self.route_change
        self.boards = self.store.get_boards()
        self.login_profile_button = ft.PopupMenuItem(text="Log in", on_click=self.login)
        self.settings = ft.PopupMenuItem(text="Settings", on_click=self.settings_popup)
        self.appbar_items = [
            self.login_profile_button,
            ft.PopupMenuItem(),  # divider
            self.settings,
        ]
        self.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.DEVELOPER_MODE),
            leading_width=100,
            title=ft.Text(
                f"UniFleet",
                font_family="Pacifico",
                size=32,
                text_align=ft.TextAlign.START,
            ),
            center_title=False,
            toolbar_height=75,
            bgcolor="#778da9",
            actions=[
                ft.Container(
                    content=ft.PopupMenuButton(items=self.appbar_items),
                    margin=ft.margin.only(left=50, right=25),
                )
            ],
        )
        self.page.appbar = self.appbar

        self.page.update()
        super().__init__(
            self,
            self.page,
            self.store,
            tight=True,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    def initialize(self):
        self.login(None)

    def login(self, e):
        def close_dlg(e):
            # Verificar se o usuário e a senha existem e correspondem
            stored_users = self.page.client_storage.get("users") or {}

            if user_name.value not in stored_users or stored_users[user_name.value] != password.value:
                password.error_text = "A senha ou usuário estão incorretos"
                user_name.border_color = ft.Colors.RED
                password.border_color = ft.Colors.RED
                self.page.update()
                return
            else:
                # Login bem-sucedido
                self.user = user_name.value
                self.page.client_storage.set("current_user", user_name.value)

                self.page.close(dialog)
                self.appbar_items[0] = ft.PopupMenuItem(
                    text=f"{self.page.client_storage.get('current_user')}'s Profile"
                )
                self.page.update()
                self.load_main_view()

        def open_register(e):
            self.page.close(dialog)
            self.register(None)

        user_name = ft.TextField(label="User name")
        password = ft.TextField(label="Password", password=True)
        login_button = ft.ElevatedButton(text="Login", on_click=close_dlg)
        register_button = ft.TextButton(text="Registrar-se", on_click=open_register)
        dialog = ft.AlertDialog(
            title=ft.Text("Please enter your login credentials"),
            content=ft.Column(
                [
                    user_name,
                    password,
                    ft.Row(
                        [login_button, register_button],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True,
            ),
            modal=True,
        )
        self.page.open(dialog)

    def register(self, e):
        def close_dlg(e):
            if user_name.value == "" or password.value == "":
                user_name.error_text = "Please provide username"
                password.error_text = "Please provide password"
                self.page.update()
                return
            else:
                # Armazenar o usuário e a senha localmente
                stored_users = self.page.client_storage.get("users") or {}
                if user_name.value in stored_users:
                    user_name.error_text = "User already exists"
                    self.page.update()
                    return
                stored_users[user_name.value] = password.value
                self.page.client_storage.set("users", stored_users)

                self.user = user_name.value
                self.page.client_storage.set("current_user", user_name.value)

                self.page.close(dialog)
                self.appbar_items[0] = ft.PopupMenuItem(
                    text=f"{self.page.client_storage.get('current_user')}'s Profile"
                )
                self.page.update()
                self.load_main_view()

        def open_login(e):
            self.page.close(dialog)
            self.login(None)

        user_name = ft.TextField(label="User name")
        password = ft.TextField(label="Password", password=True)
        register_button = ft.ElevatedButton(text="Register", on_click=close_dlg)
        login_button = ft.TextButton(text="Login", on_click=open_login)
        dialog = ft.AlertDialog(
            title=ft.Text("Register a new account"),
            content=ft.Column(
                [
                    user_name,
                    password,
                    ft.Row(
                        [register_button, login_button],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True,
            ),
            modal=True,
        )
        self.page.open(dialog)

    def load_main_view(self):
        self.page.views.append(
            ft.View(
                "/",
                [self.appbar, self],
                padding=ft.padding.all(0),
                bgcolor=self.page.bgcolor,
            )
        )
        self.page.update()
        # create an initial board for demonstration if no boards
        if len(self.boards) == 0:
            self.create_new_board("My First Board")
        self.page.go("/")

    def settings_popup(self, _):
        def close_dlg(_):
            self.page.close(dialog)
            self.page.update()

        def toggle_dark_mode(_):
            if self.page.theme_mode == ft.ThemeMode.LIGHT:
                self.page.theme_mode = ft.ThemeMode.DARK
                self.appbar.bgcolor = "#0d1b2a"
                self.page.bgcolor = "#415a77"
                dark_mode_toggle.label = "Light Mode"
            else:
                self.page.theme_mode = ft.ThemeMode.LIGHT
                self.appbar.bgcolor = "#778da9"
                self.page.bgcolor = "#e0e1dd"
                dark_mode_toggle.label = "Dark Mode"
            self.page.update()

        dark_mode_toggle = ft.Switch(
            label="Light Mode" if self.page.theme_mode == ft.ThemeMode.DARK else "Dark Mode",
            on_change=toggle_dark_mode,
            value=self.page.theme_mode == ft.ThemeMode.DARK
        )

        dialog = ft.AlertDialog(
            title=ft.Text("Settings"),
            content=ft.Column(
                [
                    dark_mode_toggle,
                    ft.ElevatedButton(text="Close", on_click=close_dlg),
                ],
                tight=True,
            ),
        )
        self.page.open(dialog)
        

    def route_change(self, e):
        troute = ft.TemplateRoute(self.page.route)
        if troute.match("/"):
            self.page.go("/boards")
        elif troute.match("/board/:id"):
            if int(troute.id) > len(self.store.get_boards()):
                self.page.go("/")
                return
            self.set_board_view(int(troute.id))
        elif troute.match("/boards"):
            self.set_all_boards_view()
        elif troute.match("/members"):
            self.set_members_view()
        self.page.update()

    def add_board(self, e):
        def close_dlg(e):
            if (hasattr(e.control, "text") and not e.control.text == "Cancel") or (
                type(e.control) is ft.TextField and e.control.value != ""
            ):
                self.create_new_board(dialog_text.value)
            self.page.close(dialog)
            self.page.update()

        def textfield_change(e):
            if dialog_text.value == "":
                create_button.disabled = True
            else:
                create_button.disabled = False
            self.page.update()

        dialog_text = ft.TextField(
            label="New Board Name", on_submit=close_dlg, on_change=textfield_change
        )
        create_button = ft.ElevatedButton(
            text="Create", bgcolor=ft.Colors.BLUE_200, on_click=close_dlg, disabled=True, color=ft.Colors.BLACK
        )
        dialog = ft.AlertDialog(
            title=ft.Text("Name your new board"),
            content=ft.Column(
                [
                    dialog_text,
                    ft.Row(
                        [
                            ft.ElevatedButton(text="Cancel", on_click=close_dlg),
                            create_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True,
            ),
        )
        self.page.open(dialog)
        dialog.open = True
        self.page.update()
        dialog_text.focus()

    def create_new_board(self, board_name):
        new_board = Board(self, self.store, board_name, self.page)
        self.store.add_board(new_board)
        self.hydrate_all_boards_view()

    def delete_board(self, e):
        self.store.remove_board(e.control.data)
        self.set_all_boards_view()


def main(page: ft.Page):

    page.title = "Flet Trello clone"
    page.padding = 0
    page.theme = ft.Theme(font_family="Verdana")
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme.page_transitions.windows = "cupertino"
    page.fonts = {"Pacifico": "Pacifico-Regular.ttf"}
    app = TrelloApp(page, InMemoryStore())
    page.add(app)
    page.update()
    app.initialize()


ft.app(target=main, assets_dir="../assets")