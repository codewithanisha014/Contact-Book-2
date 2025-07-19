import tkinter as tk
from tkinter import messagebox
import sqlite3

# Create the database and table if it doesn't exist
def setup_database():
    connection = sqlite3.connect("contacts.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT
        )
    """)
    connection.commit()
    connection.close()

# Main app class
class ContactBook:
    def __init__(self, window):
        self.window = window
        self.window.title("Contact Book")
        self.window.geometry("500x550")
        self.window.config(bg="#f0f0f0")

        #data variables
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()

        # Selected contact ID for editing or deleting
        self.selected_contact_id = None

        # UI Layout
        tk.Label(window, text="Name").pack()
        tk.Entry(window, textvariable=self.name_var).pack()

        tk.Label(window, text="Phone").pack()
        tk.Entry(window, textvariable=self.phone_var).pack()

        tk.Label(window, text="Email").pack()
        tk.Entry(window, textvariable=self.email_var).pack()

        tk.Label(window, text="Address").pack()
        tk.Entry(window, textvariable=self.address_var).pack()

        tk.Button(window, text="Add Contact", command=self.add_contact).pack(pady=5)
        tk.Button(window, text="Show Contacts", command=self.show_contacts).pack(pady=5)
        tk.Button(window, text="Search Contact", command=self.search_contact).pack(pady=5)
        tk.Button(window, text="Update Contact", command=self.update_contact).pack(pady=5)
        tk.Button(window, text="Delete Contact", command=self.delete_contact).pack(pady=5)

        self.contact_listbox = tk.Listbox(window, width=60)
        self.contact_listbox.pack(pady=10)
        self.contact_listbox.bind("<<ListboxSelect>>", self.select_contact)

    # Add a new contact
    def add_contact(self):
        name = self.name_var.get()
        phone = self.phone_var.get()

        if name and phone:
            conn = sqlite3.connect("contacts.db")
            conn.execute("INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
                         (name, phone, self.email_var.get(), self.address_var.get()))
            conn.commit()
            conn.close()
            messagebox.showinfo("Done", "Contact added!")
            self.clear_fields()
            self.show_contacts()
        else:
            messagebox.showerror("Error", "Name and phone are required!")

    # Show all saved contacts
    def show_contacts(self):
        self.contact_listbox.delete(0, tk.END)
        conn = sqlite3.connect("contacts.db")
        rows = conn.execute("SELECT * FROM contacts").fetchall()
        conn.close()

        for row in rows:
            display_text = f"{row[0]}: {row[1]} | {row[2]}"
            self.contact_listbox.insert(tk.END, display_text)

    # Search by name or phone
    def search_contact(self):
        search_term = self.name_var.get().strip()
        self.contact_listbox.delete(0, tk.END)

        conn = sqlite3.connect("contacts.db")
        query = "SELECT * FROM contacts WHERE name LIKE ? OR phone LIKE ?"
        results = conn.execute(query, (f"%{search_term}%", f"%{search_term}%")).fetchall()
        conn.close()

        for row in results:
            self.contact_listbox.insert(tk.END, f"{row[0]}: {row[1]} | {row[2]}")

    # Selecting a contact(list)
    def select_contact(self, event):
        try:
            selected = self.contact_listbox.get(self.contact_listbox.curselection())
            contact_id = selected.split(":")[0]
            self.selected_contact_id = int(contact_id)

            conn = sqlite3.connect("contacts.db")
            result = conn.execute("SELECT * FROM contacts WHERE id = ?", (self.selected_contact_id,)).fetchone()
            conn.close()

            if result:
                self.name_var.set(result[1])
                self.phone_var.set(result[2])
                self.email_var.set(result[3])
                self.address_var.set(result[4])
        except:
            pass

    # Update contact info
    def update_contact(self):
        if self.selected_contact_id:
            conn = sqlite3.connect("contacts.db")
            conn.execute("""
                UPDATE contacts
                SET name = ?, phone = ?, email = ?, address = ?
                WHERE id = ?
            """, (self.name_var.get(), self.phone_var.get(), self.email_var.get(), self.address_var.get(), self.selected_contact_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Updated", "Contact updated.")
            self.clear_fields()
            self.show_contacts()
        else:
            messagebox.showerror("Error", "Select a contact first.")

    # Delete a contact
    def delete_contact(self):
        if self.selected_contact_id:
            conn = sqlite3.connect("contacts.db")
            conn.execute("DELETE FROM contacts WHERE id = ?", (self.selected_contact_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Deleted", "Contact deleted.")
            self.clear_fields()
            self.show_contacts()
        else:
            messagebox.showerror("Error", "Select a contact to delete.")

    # Clear all entry fields
    def clear_fields(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")
        self.selected_contact_id = None

# Run the app
if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = ContactBook(root)
    root.mainloop()   