mod fs;
mod ops;

use fs::menu::create_menu;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            let menu = create_menu(app)?;
            app.set_menu(menu)?;
            Ok(())
        })
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![ops::greet::greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
