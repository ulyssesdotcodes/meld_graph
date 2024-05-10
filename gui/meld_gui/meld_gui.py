"""Welcome to Reflex! This file create a counter app."""

import reflex as rx
import random

import urllib3
import json


http = urllib3.PoolManager()


class State(rx.State):
    """The app state."""
    info: str = "loading...";
    bids_config = {
        "T1": {
            "session": '', 
               "datatype": "anat",
               "suffix": "T1w"
               },
        "FLAIR": {
            "session": '', 
                  "datatype": "anat",
                  "suffix": "FLAIR"
                  }
    }
    harmo_code = "H1"
    
    # manually synced
    demographic_info_json = []

    @rx.var
    def demographic_info(self) -> list[list[str]]:
        return list(map(lambda v: list(v.values()), self.demographic_info_json))

    def get_demographic_info(self):
        res = urllib3.request("GET", "http://meld:8080/demographic-information?name={}".format(self.harmo_code))
        self.demographic_info_json = json.loads(res.data.decode("utf-8"))
        self.info = "Loaded"

    def add_demographic_info_row(self):
        self.demographic_info_json.append(self.demographic_info_json[-1].copy())

    def update_demographic_info_cell(self, pos, data):
        print("update", pos, data)
        current = self.demographic_info_json[pos[1]]
        current[list(current.keys())[pos[0]]] = data["data"]

    def update_demographic_info(self):
        self.demographic_info_json =  [dict(zip(v.keys(), self.demographic_info[i])) for i,v in enumerate(self.demographic_info_json)]
        response = urllib3.request("POST", "http://meld:8080/demographic-information?name={}".format(self.harmo_code),
                                   headers={'Content-Type': 'application/json'},
                                   body=json.dumps(self.get_value(self.demographic_info_json)))
        self.info = response.json()["message"]

    def compute_harmo_params(self):
        response = urllib3.request("GET", "http://meld:8080/compute-harmo?name={}".format(self.harmo_code))
        self.info = response.json()["message"]

    def update_bids_config(self):
        response = urllib3.request("POST", "http://meld:8080/bids-config",
                                   headers={'Content-Type': 'application/json'},
                                   body=json.dumps(self.get_value(self.bids_config)))
        self.data = response.data.decode("utf-8")


@rx.page(on_load=State.get_demographic_info)
def index():
    """The main view."""
    return rx.vstack(
            rx.heading("Meld classifier"),
            rx.hstack(
                rx.text("Harmo code"),
                rx.input(
                    id="harmo_code",
                    placeholder="Harmo code",
                    value=State.harmo_code,
                    on_change=State.set_harmo_code
                ),
                rx.button("Fetch", on_click=State.get_demographic_info)
            ),
            rx.data_editor(
                data = State.demographic_info,
                columns = ["ID", "Code", "Group", "Age", "Sex", "Scanner"],
                on_cell_edited=State.update_demographic_info_cell
                ),
            rx.hstack(
                rx.button(
                    "Add row",
                    on_click=State.add_demographic_info_row
                    ),
                rx.button(
                    "Update",
                    on_click=State.update_demographic_info
                    ),
                rx.button(
                    "Compute harmonisation parameters",
                    on_click=State.compute_harmo_params
                    ),
            ),
            rx.chakra.alert(
                rx.chakra.alert_title(State.info),
                status="info"
                ),
            align="center",
            padding="1em",
            bg="#ededed",
            border_radius="1em",
        )

app = rx.App()
app.add_page(index, title="Counter")
