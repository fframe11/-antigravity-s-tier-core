Drive a real or simulated iOS/Android device.

Start with mobile_list_available_devices and pass the chosen device id to every
later call - there is no implicit "current device". Use a remote device only
when local ones do not fit or when requested by the user. Remote devices cost
money and take time to allocate and release. Release when done using, so the
remote device cleans and returns to pool.

Read the screen with mobile_list_elements_on_screen, not screenshots: it returns
refs, coordinates and labels, and tapping by ref survives layout differences
between devices. Fall back to mobile_take_screenshot only for elements missing
from the hierarchy, or to judge visual appearance.

Each call is a device round-trip. Group known sequences (tap, type, tap) into
mobile_batch_commands instead of issuing them one at a time.

Prefer mobile_launch_app to open an app, and mobile_open_url to open a web page,
over navigating through the UI. mobile_open_url only accepts http:// and
https:// URLs unless the server was started with MOBILEMCP_ALLOW_UNSAFE_URLS=1,
so do not rely on it for app deep links.