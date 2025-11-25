import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import psycopg2
from datetime import date

DB_CONFIG = {
    "host": "localhost",
    "database": "library_db",
    "user": "postgres",
    "password": 123
}

class LibrarySystem(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Library Management system")
        self.geometry("1600x900")
        
        self.setup_styles()
        self.create_layout()
        
    def setup_styles(self):
        pass

    def get_db_connection(self):
        try:
            return psycopg2.connect(**DB_CONFIG)
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            return None

    def create_layout(self):
        self.dashboard_frame = ttk.Frame(self, bootstyle="secondary", padding=10)
        self.dashboard_frame.pack(fill=X)
        
        self.lbl_stats = ttk.Label(self.dashboard_frame, text="Loading Stats...", font=("Helvetica", 12, "bold"), bootstyle="inverse-secondary")
        self.lbl_stats.pack(side=LEFT)
        
        ttk.Button(self.dashboard_frame, text="Refresh Data", command=self.refresh_all, bootstyle="dark-outline").pack(side=RIGHT)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.tab_books = ttk.Frame(self.tabs)
        self.tab_members = ttk.Frame(self.tabs)
        self.tab_loans = ttk.Frame(self.tabs)

        self.tabs.add(self.tab_books, text=" Books ")
        self.tabs.add(self.tab_members, text=" Members ")
        self.tabs.add(self.tab_loans, text=" Loans ")

        self.setup_books_tab()
        self.setup_members_tab()
        self.setup_loans_tab()
        
        self.refresh_all()

    def refresh_all(self):
        self.update_dashboard()
        self.load_books()
        self.load_members()
        self.load_loans()
        self.update_loan_dropdowns()

    def update_dashboard(self):
        conn = self.get_db_connection()
        if not conn: return
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM books")
        total_books = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM members")
        total_members = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM loans WHERE return_date IS NULL")
        active_loans = cur.fetchone()[0]
        
        stats_text = f"Total Books: {total_books}   |   Members: {total_members}   |   Active Loans: {active_loans}"
        self.lbl_stats.config(text=stats_text)
        
        conn.close()

    def setup_books_tab(self):
        input_frame = ttk.Labelframe(self.tab_books, text="Add / Delete Book", padding=10)
        input_frame.pack(fill=X, padx=10, pady=5)

        grid_opts = {'padx': 5, 'pady': 5, 'sticky': W}
        
        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, **grid_opts)
        self.ent_book_title = ttk.Entry(input_frame, width=30)
        self.ent_book_title.grid(row=0, column=1, **grid_opts)

        ttk.Label(input_frame, text="Author:").grid(row=0, column=2, **grid_opts)
        self.ent_book_author = ttk.Entry(input_frame, width=30)
        self.ent_book_author.grid(row=0, column=3, **grid_opts)

        ttk.Label(input_frame, text="ISBN:").grid(row=1, column=0, **grid_opts)
        self.ent_book_isbn = ttk.Entry(input_frame, width=30)
        self.ent_book_isbn.grid(row=1, column=1, **grid_opts)

        ttk.Label(input_frame, text="Stock:").grid(row=1, column=2, **grid_opts)
        self.ent_book_stock = ttk.Spinbox(input_frame, from_=0, to=1000, width=10)
        self.ent_book_stock.grid(row=1, column=3, **grid_opts)
        self.ent_book_stock.set(1)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=0, column=4, rowspan=2, padx=20)
        
        ttk.Button(btn_frame, text="Add Book", command=self.add_book, bootstyle="success").pack(fill=X, pady=2)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_book, bootstyle="danger").pack(fill=X, pady=2)

        search_frame = ttk.Frame(self.tab_books, padding=5)
        search_frame.pack(fill=X, padx=10)
        ttk.Label(search_frame, text="Search:").pack(side=LEFT)
        self.ent_search_book = ttk.Entry(search_frame)
        self.ent_search_book.pack(side=LEFT, padx=5, fill=X, expand=True)
        ttk.Button(search_frame, text="Find", command=self.search_books, bootstyle="info-outline").pack(side=LEFT)

        self.tree_books = ttk.Treeview(self.tab_books, columns=("ID", "Title", "Author", "ISBN", "Stock"), show='headings', height=15)
        self.tree_books.heading("ID", text="ID")
        self.tree_books.column("ID", width=50)
        self.tree_books.heading("Title", text="Title")
        self.tree_books.column("Title", width=300)
        self.tree_books.heading("Author", text="Author")
        self.tree_books.heading("ISBN", text="ISBN")
        self.tree_books.heading("Stock", text="Stock")
        self.tree_books.column("Stock", width=80)
        
        self.tree_books.pack(fill=BOTH, expand=True, padx=10, pady=5)

    def add_book(self):
        title = self.ent_book_title.get()
        author = self.ent_book_author.get()
        isbn = self.ent_book_isbn.get()
        stock = self.ent_book_stock.get()
        
        if not title or not author or not isbn:
            messagebox.showwarning("Error", "Title, Author, and ISBN are required")
            return

        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO books (title, author, isbn, stock_quantity) VALUES (%s, %s, %s, %s)", 
                    (title, author, isbn, stock)
                )
                conn.commit()
                self.refresh_all()
                
                self.ent_book_title.delete(0, END)
                self.ent_book_author.delete(0, END)
                self.ent_book_isbn.delete(0, END)
                self.ent_book_stock.set(1)
                
            except psycopg2.IntegrityError:
                conn.rollback()
                messagebox.showerror("Error", "That ISBN already exists in the database!")
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

    def delete_book(self):
        selected = self.tree_books.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a book to delete")
            return
        
        book_id = self.tree_books.item(selected[0])['values'][0]
        
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
                conn.commit()
                self.refresh_all()
            except psycopg2.IntegrityError:
                messagebox.showerror("Error", "Cannot delete book. It might be currently referenced in a loan record.")
            finally:
                conn.close()

    def load_books(self):
        self._populate_tree(self.tree_books, "SELECT book_id, title, author, isbn, stock_quantity FROM books ORDER BY book_id ASC")

    def search_books(self):
        query = self.ent_search_book.get()
        sql = "SELECT book_id, title, author, isbn, stock_quantity FROM books WHERE title ILIKE %s OR author ILIKE %s"
        self._populate_tree(self.tree_books, sql, (f'%{query}%', f'%{query}%'))

    def setup_members_tab(self):
        input_frame = ttk.Labelframe(self.tab_members, text="Manage Members", padding=10)
        input_frame.pack(fill=X, padx=10, pady=5)

        ttk.Label(input_frame, text="Name:").pack(side=LEFT, padx=5)
        self.ent_mem_name = ttk.Entry(input_frame)
        self.ent_mem_name.pack(side=LEFT, padx=5)

        ttk.Label(input_frame, text="Email:").pack(side=LEFT, padx=5)
        self.ent_mem_email = ttk.Entry(input_frame)
        self.ent_mem_email.pack(side=LEFT, padx=5)

        ttk.Button(input_frame, text="Add Member", command=self.add_member, bootstyle="success").pack(side=LEFT, padx=10)

        search_frame = ttk.Frame(self.tab_members, padding=5)
        search_frame.pack(fill=X, padx=10)
        
        ttk.Label(search_frame, text="Search Member:").pack(side=LEFT)
        self.ent_search_member = ttk.Entry(search_frame)
        self.ent_search_member.pack(side=LEFT, padx=5, fill=X, expand=True)
        ttk.Button(search_frame, text="Find", command=self.search_members, bootstyle="info-outline").pack(side=LEFT)

        self.tree_members = ttk.Treeview(self.tab_members, columns=("ID", "Name", "Email", "Phone"), show='headings')
        self.tree_members.heading("ID", text="ID")
        self.tree_members.heading("Name", text="Name")
        self.tree_members.heading("Email", text="Email")
        self.tree_members.heading("Phone", text="Phone")
        self.tree_members.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def add_member(self):
        name = self.ent_mem_name.get()
        email = self.ent_mem_email.get()
        if name and email:
            conn = self.get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO members (name, email) VALUES (%s, %s)", (name, email))
                conn.commit()
                self.refresh_all()
                self.ent_mem_name.delete(0, END)
                self.ent_mem_email.delete(0, END)
            except psycopg2.IntegrityError:
                messagebox.showerror("Error", "Email already exists")
            finally:
                conn.close()

    def load_members(self):
        self._populate_tree(self.tree_members, "SELECT member_id, name, email, phone FROM members ORDER BY member_id ASC")

    def search_members(self):
        query = self.ent_search_member.get()
        sql = """
            SELECT member_id, name, email, phone 
            FROM members 
            WHERE name ILIKE %s OR email ILIKE %s
            ORDER BY member_id ASC
        """
        self._populate_tree(self.tree_members, sql, (f'%{query}%', f'%{query}%'))

    def setup_loans_tab(self):
        issue_frame = ttk.Labelframe(self.tab_loans, text="Issue New Book", padding=15)
        issue_frame.pack(fill=X, padx=10, pady=5)
        
        ttk.Label(issue_frame, text="Select Book:").grid(row=0, column=0, padx=5)
        self.cbo_books = ttk.Combobox(issue_frame, width=40, state="readonly")
        self.cbo_books.grid(row=0, column=1, padx=5)

        ttk.Label(issue_frame, text="Select Member:").grid(row=0, column=2, padx=5)
        self.cbo_members = ttk.Combobox(issue_frame, width=30, state="readonly")
        self.cbo_members.grid(row=0, column=3, padx=5)

        ttk.Button(issue_frame, text="Issue Book", command=self.issue_book, bootstyle="warning").grid(row=0, column=4, padx=15)

        list_frame = ttk.Frame(self.tab_loans)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        self.var_show_active = tk.BooleanVar(value=True)
        ttk.Checkbutton(list_frame, text="Show Active Only", variable=self.var_show_active, command=self.load_loans, bootstyle="round-toggle").pack(anchor=W)

        self.tree_loans = ttk.Treeview(list_frame, columns=("LoanID", "Book", "Member", "IssueDate", "ReturnDate", "Action"), show='headings')
        self.tree_loans.heading("LoanID", text="ID")
        self.tree_loans.column("LoanID", width=50)
        self.tree_loans.heading("Book", text="Book Title")
        self.tree_loans.column("Book", width=250)
        self.tree_loans.heading("Member", text="Member Name")
        self.tree_loans.heading("IssueDate", text="Issued")
        self.tree_loans.heading("ReturnDate", text="Returned")
        self.tree_loans.heading("Action", text="Status")
        
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.tree_loans.yview)
        self.tree_loans.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree_loans.pack(fill=BOTH, expand=True)

        ttk.Label(list_frame, text="* Right-click on a row to Return Book", font=("Arial", 8, "italic")).pack(anchor=W)
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Return This Book", command=self.return_book_context)
        self.tree_loans.bind("<Button-3>", self.show_context_menu)

    def update_loan_dropdowns(self):
        conn = self.get_db_connection()
        if conn:
            cur = conn.cursor()
            
            cur.execute("SELECT book_id, title FROM books WHERE stock_quantity > 0 ORDER BY title")
            self.books_map = {f"{row[0]} - {row[1]}": row[0] for row in cur.fetchall()}
            self.cbo_books['values'] = list(self.books_map.keys())

            cur.execute("SELECT member_id, name FROM members ORDER BY name")
            self.members_map = {f"{row[0]} - {row[1]}": row[0] for row in cur.fetchall()}
            self.cbo_members['values'] = list(self.members_map.keys())
            
            conn.close()

    def issue_book(self):
        book_str = self.cbo_books.get()
        mem_str = self.cbo_members.get()

        if not book_str or not mem_str:
            messagebox.showwarning("Input", "Please select both a book and a member.")
            return

        book_id = self.books_map[book_str]
        member_id = self.members_map[mem_str]

        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("UPDATE books SET stock_quantity = stock_quantity - 1 WHERE book_id = %s", (book_id,))
                cur.execute("INSERT INTO loans (book_id, member_id, loan_date) VALUES (%s, %s, %s)", 
                            (book_id, member_id, date.today()))
                conn.commit()
                messagebox.showinfo("Success", "Book Issued Successfully")
                self.refresh_all()
                self.cbo_books.set('')
                self.cbo_members.set('')
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

    def show_context_menu(self, event):
        item = self.tree_loans.identify_row(event.y)
        if item:
            self.tree_loans.selection_set(item)
            vals = self.tree_loans.item(item)['values']
            if vals[4] == "Pending":
                self.context_menu.post(event.x_root, event.y_root)

    def return_book_context(self):
        selected = self.tree_loans.selection()
        if not selected: return
        
        loan_id = self.tree_loans.item(selected[0])['values'][0]
        
        conn = self.get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT book_id FROM loans WHERE loan_id = %s", (loan_id,))
                book_id = cur.fetchone()[0]
                cur.execute("UPDATE loans SET return_date = %s WHERE loan_id = %s", (date.today(), loan_id))
                cur.execute("UPDATE books SET stock_quantity = stock_quantity + 1 WHERE book_id = %s", (book_id,))
                conn.commit()

                messagebox.showinfo("Success", "Book Returned")
                self.refresh_all()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()

    def load_loans(self):
        for i in self.tree_loans.get_children():
            self.tree_loans.delete(i)
        
        conn = self.get_db_connection()
        if conn:
            cur = conn.cursor()
            
            base_query = """
                SELECT l.loan_id, b.title, m.name, l.loan_date, l.return_date 
                FROM loans l
                JOIN books b ON l.book_id = b.book_id
                JOIN members m ON l.member_id = m.member_id
            """
            
            if self.var_show_active.get():
                base_query += " WHERE l.return_date IS NULL"
            
            base_query += " ORDER BY l.loan_id ASC"
            
            cur.execute(base_query)
            rows = cur.fetchall()
            
            for row in rows:
                r_list = list(row)
                if r_list[4] is None:
                    r_list[4] = "Pending"
                    status = "😔 Out"
                else:
                    status = "😊 In"
                
                r_list.append(status)
                self.tree_loans.insert("", END, values=r_list)
            conn.close()

    def _populate_tree(self, tree, query, params=None):
        for i in tree.get_children():
            tree.delete(i)
        conn = self.get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute(query, params or ())
            for row in cur.fetchall():
                tree.insert("", END, values=row)
            conn.close()

if __name__ == "__main__":
    app = LibrarySystem()
    app.mainloop()