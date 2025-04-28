import phonenumbers
from phonenumbers import timezone, geocoder, carrier
import folium
from opencage.geocoder import OpenCageGeocode
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser
from datetime import datetime


class AdvancedPhoneTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Phone Tracker")
        self.root.geometry("650x550")

        # API Configuration
        self.api_key = "6b1c8b12457f4b5caeec3644a4c5d386"  # Replace with your actual API key
        self.geocoder = OpenCageGeocode(self.api_key)

        self.create_widgets()
        self.current_map_path = None

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=5)

        ttk.Label(header_frame, text="Phone Number:", font=('Arial', 10)).pack(side=tk.LEFT)
        self.phone_entry = ttk.Entry(header_frame, width=25, font=('Arial', 10))
        self.phone_entry.pack(side=tk.LEFT, padx=10)

        ttk.Button(header_frame, text="Track", command=self.track_number).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Clear", command=self.clear_fields).pack(side=tk.LEFT, padx=5)

        # Results Notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)

        # Basic Info Tab
        basic_tab = ttk.Frame(self.notebook)
        self.notebook.add(basic_tab, text="Basic Info")

        self.basic_info_text = tk.Text(basic_tab, wrap=tk.WORD, height=10, padx=5, pady=5)
        self.basic_info_text.pack(fill=tk.BOTH, expand=True)

        # Location Tab
        location_tab = ttk.Frame(self.notebook)
        self.notebook.add(location_tab, text="Location")

        self.location_info_text = tk.Text(location_tab, wrap=tk.WORD, height=10, padx=5, pady=5)
        self.location_info_text.pack(fill=tk.BOTH, expand=True)

        # Map Frame
        map_frame = ttk.Frame(main_frame)
        map_frame.pack(fill=tk.X, pady=5)

        ttk.Button(map_frame, text="Save Map", command=self.save_map, state=tk.DISABLED).pack(side=tk.LEFT)
        self.save_map_btn = ttk.Button(map_frame, text="View Map", command=self.view_map, state=tk.DISABLED)
        self.save_map_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(map_frame, text="Open in Browser", command=self.open_in_browser, state=tk.DISABLED).pack(
            side=tk.LEFT)
        self.open_browser_btn = ttk.Button(map_frame, text="Open in Browser", command=self.open_in_browser,
                                           state=tk.DISABLED)

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X)

    def track_number(self):
        phone_number = self.phone_entry.get().strip()
        if not phone_number:
            messagebox.showerror("Error", "Please enter a phone number")
            return

        try:
            # Clear previous results
            self.basic_info_text.delete(1.0, tk.END)
            self.location_info_text.delete(1.0, tk.END)
            self.status_var.set("Processing...")
            self.root.update()

            # Parse phone number
            parsed_number = phonenumbers.parse(phone_number)
            national_number = parsed_number.national_number
            country_code = parsed_number.country_code

            # Get basic info
            time_zones = timezone.time_zones_for_number(parsed_number)
            carrier_name = carrier.name_for_number(parsed_number, 'en')
            region = geocoder.description_for_number(parsed_number, 'en')

            # Display basic info
            self.basic_info_text.insert(tk.END, f"📱 Phone Number: +{country_code} {national_number}\n")
            self.basic_info_text.insert(tk.END, f"⏰ Timezone(s): {', '.join(time_zones)}\n")
            self.basic_info_text.insert(tk.END, f"📶 Carrier: {carrier_name}\n")
            self.basic_info_text.insert(tk.END, f"🌍 Region: {region}\n")

            # Get detailed location
            query = f"{carrier_name} {region}"
            results = self.geocoder.geocode(query)

            if results and len(results) > 0:
                result = results[0]
                components = result.get('components', {})
                geometry = result.get('geometry', {})

                # Display location info
                self.location_info_text.insert(tk.END, "📍 Detailed Location:\n")
                self.location_info_text.insert(tk.END, f"🏙️ City: {components.get('city', 'N/A')}\n")
                self.location_info_text.insert(tk.END, f"🏘️ District: {components.get('district', 'N/A')}\n")
                self.location_info_text.insert(tk.END, f"🏢 State: {components.get('state', 'N/A')}\n")
                self.location_info_text.insert(tk.END, f"🇺🇳 Country: {components.get('country', 'N/A')}\n")
                self.location_info_text.insert(tk.END, f"📪 Postal Code: {components.get('postcode', 'N/A')}\n\n")
                self.location_info_text.insert(tk.END, f"🗺️ Formatted Address:\n{result.get('formatted', 'N/A')}\n")

                # Create map
                lat, lng = geometry.get('lat', 0), geometry.get('lng', 0)
                if lat and lng:
                    self.create_map(lat, lng, f"+{country_code} {national_number}")
                    self.save_map_btn.config(state=tk.NORMAL)
                    self.open_browser_btn.config(state=tk.NORMAL)

            self.status_var.set(f"Last tracked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except Exception as e:
            messagebox.showerror("Error", f"Tracking failed: {str(e)}")
            self.status_var.set("Error occurred")

    def create_map(self, lat, lng, number):
        self.map = folium.Map(location=[lat, lng], zoom_start=12)
        folium.Marker(
            [lat, lng],
            popup=f"Phone: {number}",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(self.map)

        # Add circle for approximate area
        folium.Circle(
            radius=5000,  # 5km radius (approximation)
            location=[lat, lng],
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.2
        ).add_to(self.map)

        self.current_map_path = "temp_phone_location.html"
        self.map.save(self.current_map_path)

    def save_map(self):
        if not hasattr(self, 'map'):
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")],
            title="Save Phone Location Map"
        )

        if file_path:
            try:
                self.map.save(file_path)
                messagebox.showinfo("Success", f"Map saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save map: {str(e)}")

    def view_map(self):
        if self.current_map_path:
            webbrowser.open_new_tab(f"file://{os.path.abspath(self.current_map_path)}")

    def open_in_browser(self):
        if hasattr(self, 'map') and self.current_map_path:
            webbrowser.open_new_tab(f"file://{os.path.abspath(self.current_map_path)}")

    def clear_fields(self):
        self.phone_entry.delete(0, tk.END)
        self.basic_info_text.delete(1.0, tk.END)
        self.location_info_text.delete(1.0, tk.END)
        self.save_map_btn.config(state=tk.DISABLED)
        self.open_browser_btn.config(state=tk.DISABLED)
        self.status_var.set("Ready")

        # Clean up temp file
        if self.current_map_path and os.path.exists(self.current_map_path):
            try:
                os.remove(self.current_map_path)
            except:
                pass
        self.current_map_path = None


if __name__ == "__main__":
    import os

    root = tk.Tk()
    app = AdvancedPhoneTracker(root)
    root.mainloop()
