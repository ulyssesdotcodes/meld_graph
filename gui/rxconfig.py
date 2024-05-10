import reflex as rx

config = rx.Config(
    app_name="meld_gui",
    db_url="sqlite:///reflex.db",
    env=rx.Env.DEV,
)
