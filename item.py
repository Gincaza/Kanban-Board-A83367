from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board_list import BoardList
import itertools
import flet as ft
from data_store import DataStore


class Item(ft.Container):
    id_counter = itertools.count()

    def __init__(self, list: "BoardList", store: DataStore, item_text: str, labels: list[str] = None):
        self.item_id = next(Item.id_counter)
        self.store: DataStore = store
        self.list = list
        self.item_text = item_text
        self.labels = labels if labels else []

        self.menu_button = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(
                    text="Edit",
                    icon=ft.Icons.EDIT,
                    on_click=self.edit_item
                ),
                ft.PopupMenuItem(
                    text="Delete",
                    icon=ft.Icons.DELETE,
                    on_click=self.delete_item
                ),
                ft.PopupMenuItem(
                    text="Manage Labels",
                    icon=ft.Icons.LABEL,
                    on_click=self.manage_labels
                ),
            ]
        )

        self.card_item = ft.Card(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Checkbox(label=f"{self.item_text}", width=200),
                                border_radius=ft.border_radius.all(5),
                                expand=True,
                            ),
                            self.menu_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            ft.Text(label, bgcolor=ft.Colors.LIGHT_BLUE)
                            for label in self.labels
                        ],
                        wrap=True,
                    ),
                ],
                spacing=5,
            ),
            elevation=1,
            data=self,
        )
        self.view = ft.Draggable(
            group="items",
            content=ft.DragTarget(
                group="items",
                content=self.card_item,
                on_accept=self.drag_accept,
                on_leave=self.drag_leave,
                on_will_accept=self.drag_will_accept,
            ),
            data=self,
        )
        super().__init__(content=self.view)

    def manage_labels(self, e):
        def close_dlg(e):
            self.labels = [label_field.value]
            self.card_item.content.controls[1].controls = [
                ft.Text(label, bgcolor=ft.Colors.LIGHT_BLUE)
                for label in self.labels
            ]
            self.page.close(dialog)
            self.page.update()

        label_field = ft.TextField(value=self.labels[0] if self.labels else "", hint_text="Add or edit label")

        dialog = ft.AlertDialog(
            title=ft.Text("Manage Label"),
            content=ft.Column(
                [label_field, ft.ElevatedButton(text="Save", on_click=close_dlg)],
                tight=True,
            ),
        )
        self.page.open(dialog)

    def drag_accept(self, e):
        src = self.page.get_control(e.src_id)

        # skip if item is dropped on itself
        if src.content.content == e.control.content:
            self.card_item.elevation = 1
            self.list.set_indicator_opacity(self, 0.0)
            e.control.update()
            return

        # item dropped within same list but not on self
        if src.data.list == self.list:
            self.list.add_item(chosen_control=src.data, swap_control=self)
            self.card_item.elevation = 1
            e.control.update()
            return

        # item added to different list
        new_item = Item(self.list, self.store, src.data.item_text, labels=src.data.labels)
        self.list.add_item(new_item)
        # remove from the list to which draggable belongs
        src.data.list.remove_item(src.data)
        self.list.set_indicator_opacity(self, 0.0)
        self.card_item.elevation = 1
        self.page.update()

    def drag_will_accept(self, e):
        if e.data == "true":
            self.list.set_indicator_opacity(self, 1.0)
        self.card_item.elevation = 20 if e.data == "true" else 1
        self.page.update()

    def drag_leave(self, e):
        self.list.set_indicator_opacity(self, 0.0)
        self.card_item.elevation = 1
        self.page.update()
    
    def edit_item(self, e):
        self.card_item.content.controls[0].controls[0].content = ft.TextField(
            value=self.item_text,
            on_submit=self.save_item,
        )
        self.page.update()
    
    def save_item(self, e):
        # Atualizar o texto do item
        self.item_text = e.control.value
        self.card_item.content.controls[0].controls[0].content = ft.Checkbox(
            label=f"{self.item_text}", width=200
        )

        # Atualizar o client_storage
        stored_users, current_user_data = self.list.board.app.get_current_user_data()
        if current_user_data:
            boards = current_user_data.get("boards") or {}
            board_data = boards.get(str(self.list.board.board_id)) or {}
            lists = board_data.get("lists") or {}
            list_data = lists.get(str(self.list.board_list_id)) or {}
            items = list_data.get("items", {})
            if str(self.item_id) in items:
                items[str(self.item_id)]["text"] = self.item_text  # Atualizar o texto do item
            list_data["items"] = items
            lists[str(self.list.board_list_id)] = list_data
            board_data["lists"] = lists
            boards[str(self.list.board.board_id)] = board_data
            current_user_data["boards"] = boards
            stored_users[self.page.client_storage.get("current_user")] = current_user_data
            self.page.client_storage.set("users", stored_users)

        # Atualizar a interface
        self.page.update()
    
    def delete_item(self, e):
        self.list.remove_item(self)