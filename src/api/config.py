from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str = "nona"
    items_per_user: int = 50
    data_process_dir_path: str = "\\src\\data\\processing-batch\\data-process\\"
    tool_path: str = "\\src\\data\\processing-batch\\pos_tools\\"
    trained_model_path: str = "\\models\\"

    model_config = SettingsConfigDict(env_file=".env")