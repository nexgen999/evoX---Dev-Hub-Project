import json
import os
import urllib.request
import tkinter as tk
from tkinter import ttk, messagebox

# Banque d'icônes FontAwesome courantes
ICON_PRESETS = [
    ("Xbox", "fa-brands fa-xbox"),
    ("PlayStation", "fa-brands fa-playstation"),
    ("Windows", "fa-brands fa-windows"),
    ("Apple", "fa-brands fa-apple"),
    ("Android", "fa-brands fa-android"),
    ("Linux", "fa-brands fa-linux"),
    ("GitHub", "fa-brands fa-github"),
    ("Twitter / X", "fa-brands fa-x-twitter"),
    ("YouTube", "fa-brands fa-youtube"),
    ("Discord", "fa-brands fa-discord"),
    ("Globe / Web", "fa-solid fa-globe"),
    ("Outils / Clé", "fa-solid fa-wrench"),
    ("Dossier", "fa-solid fa-folder"),
    ("Code", "fa-solid fa-code"),
    ("Terminal", "fa-solid fa-terminal"),
    ("Serveur", "fa-solid fa-server"),
    ("Étoile", "fa-solid fa-star"),
    ("Enveloppe / Mail", "fa-solid fa-envelope")
]

class IconPickerPopup(tk.Toplevel):
    """Fenêtre de sélection rapide d'icônes FontAwesome"""
    def __init__(self, parent, target_entry):
        super().__init__(parent)
        self.title("Choisir une icône")
        self.geometry("400x350")
        self.configure(bg="#0f172a")
        self.target_entry = target_entry

        ttk.Label(self, text="Sélectionne une icône FontAwesome :", font=("Segoe UI", 10, "bold")).pack(pady=10)

        listbox_frame = ttk.Frame(self)
        listbox_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.listbox = tk.Listbox(
            listbox_frame, bg="#1e293b", fg="#ffffff",
            selectbackground="#2563eb", selectforeground="#ffffff",
            font=("Segoe UI", 10), borderwidth=0
        )
        self.listbox.pack(fill="both", expand=True)

        for label, icon_code in ICON_PRESETS:
            self.listbox.insert(tk.END, f"{label}  ➔  {icon_code}")

        ttk.Button(self, text="Valider la sélection", command=self.apply_selection).pack(pady=10)

    def apply_selection(self):
        sel = self.listbox.curselection()
        if sel:
            icon_code = ICON_PRESETS[sel[0]][1]
            self.target_entry.delete(0, tk.END)
            self.target_entry.insert(0, icon_code)
        self.destroy()

class ProjectPreviewPopup(tk.Toplevel):
    """Popup de prévisualisation complète d'un dépôt GitHub"""
    def __init__(self, parent, project_data):
        super().__init__(parent)
        self.title(f"Aperçu — {project_data.get('title', 'Dépôt')}")
        self.geometry("650x550")
        self.configure(bg="#0f172a")

        github_url = project_data.get("github", "")

        # Zone Header
        header = ttk.Frame(self, style="Card.TFrame", padding=15)
        header.pack(fill="x", padx=15, pady=15)

        ttk.Label(header, text=project_data.get("title", ""), font=("Segoe UI", 14, "bold"), style="Card.TLabel").pack(anchor="w")
        ttk.Label(header, text=project_data.get("description", "Aucune description."), style="Card.TLabel", wraplength=580).pack(anchor="w", pady=(5, 10))

        # Stats GitHub (depuis l'API ou fallback)
        self.stats_frame = ttk.Frame(header, style="Card.TFrame")
        self.stats_frame.pack(anchor="w")

        self.stars_lbl = ttk.Label(self.stats_frame, text="⭐ Stars: ...", style="Card.TLabel")
        self.stars_lbl.pack(side="left", padx=(0, 15))
        self.forks_lbl = ttk.Label(self.stats_frame, text="🍴 Forks: ...", style="Card.TLabel")
        self.forks_lbl.pack(side="left", padx=(0, 15))
        self.issues_lbl = ttk.Label(self.stats_frame, text="🐛 Issues: ...", style="Card.TLabel")
        self.issues_lbl.pack(side="left")

        # Zone README / Infos
        body = ttk.Frame(self, style="Card.TFrame", padding=15)
        body.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        ttk.Label(body, text="📄 README.md / Contenu :", font=("Segoe UI", 10, "bold"), style="Card.TLabel").pack(anchor="w", pady=(0, 5))

        self.readme_text = tk.Text(body, bg="#0f172a", fg="#f8fafc", insertbackground="#ffffff", borderwidth=0, font=("Consolas", 9), wrap="word")
        self.readme_text.pack(fill="both", expand=True)

        if github_url:
            self.fetch_github_details(github_url)
        else:
            self.readme_text.insert("1.0", "Aucun lien GitHub renseigné pour ce dépôt.")

    def fetch_github_details(self, repo_url):
        try:
            # Extraire "user/repo" depuis l'URL
            parts = repo_url.rstrip("/").split("/")
            if len(parts) >= 2:
                owner, repo = parts[-2], parts[-1]
                api_url = f"https://api.github.com/repos/{owner}/{repo}"

                req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode())
                    self.stars_lbl.config(text=f"⭐ Stars: {data.get('stargazers_count', 0)}")
                    self.forks_lbl.config(text=f"🍴 Forks: {data.get('forks_count', 0)}")
                    self.issues_lbl.config(text=f"🐛 Issues: {data.get('open_issues_count', 0)}")

                # Tenter de charger le README
                readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
                req_rm = urllib.request.Request(readme_url, headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    with urllib.request.urlopen(req_rm) as resp_rm:
                        content = resp_rm.read().decode('utf-8')
                        self.readme_text.insert("1.0", content)
                except Exception:
                    self.readme_text.insert("1.0", "Impossible de charger le fichier README.md directement.")
        except Exception as e:
            self.readme_text.insert("1.0", f"Erreur lors de la récupération GitHub : {e}")

class NexgenStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("nexgen — Studio de Gestion")
        self.root.geometry("1200x800")

        self.setup_styles()
        self.create_text_context_menu()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.cat_data = self.load_json("categories.json", [])
        self.proj_data = self.load_json("projects.json", [])
        self.socials_data = self.load_json("socials.json", [])

        self.init_profile_tab()
        self.init_categories_tab()
        self.init_projects_tab()
        self.init_socials_tab()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        bg_main, bg_card, fg_text, accent_blue = "#0f172a", "#1e293b", "#f8fafc", "#2563eb"
        self.root.configure(bg=bg_main)

        style.configure(".", background=bg_main, foreground=fg_text, font=("Segoe UI", 9))
        style.configure("TNotebook", background=bg_main, borderwidth=0)
        style.configure("TNotebook.Tab", background=bg_card, foreground="#94a3b8", padding=[14, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", accent_blue)], foreground=[("selected", "#ffffff")])

        style.configure("TFrame", background=bg_main)
        style.configure("Card.TFrame", background=bg_card, relief="flat")
        style.configure("TLabel", background=bg_main, foreground=fg_text)
        style.configure("Card.TLabel", background=bg_card, foreground=fg_text)

        style.configure("TButton", background=accent_blue, foreground="#ffffff", borderwidth=0, padding=6, font=("Segoe UI", 9, "bold"))
        style.map("TButton", background=[("active", "#1d4ed8")])

        style.configure("TEntry", fieldbackground="#0f172a", foreground="#ffffff", insertcolor="#ffffff", borderwidth=1, bordercolor="#334155")
        style.configure("Treeview", background="#1e293b", foreground="#ffffff", fieldbackground="#1e293b", rowheight=28)
        style.configure("Treeview.Heading", background="#334155", foreground="#ffffff", font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", accent_blue)], foreground=[("selected", "#ffffff")])

    def create_text_context_menu(self):
        self.text_menu = tk.Menu(self.root, tearoff=0)
        self.text_menu.add_command(label="Couper", command=lambda: self.root.focus_get().event_generate("<<Cut>>"))
        self.text_menu.add_command(label="Copier", command=lambda: self.root.focus_get().event_generate("<<Copy>>"))
        self.text_menu.add_command(label="Coller", command=lambda: self.root.focus_get().event_generate("<<Paste>>"))
        self.root.bind_class("Entry", "<Button-3>", lambda e: self.text_menu.post(e.x_root, e.y_root))

    def load_json(self, path, fallback):
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return fallback

    def save_json(self, path, data):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Succès", f"Sauvegardé dans {path} !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur de sauvegarde : {e}")

    # ==================== PROFIL & GITHUB ====================
    def init_profile_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👤 Profil & GitHub")
        data = self.load_json("profile.json", {"username": "nexgen", "handle": "nexgen_dev", "avatar": "", "bio": ""})

        card = ttk.Frame(tab, style="Card.TFrame", padding=20)
        card.pack(fill="x", padx=15, pady=15)

        ttk.Label(card, text="Nom d'utilisateur GitHub :", style="Card.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 2))
        
        gh_frame = ttk.Frame(card, style="Card.TFrame")
        gh_frame.pack(fill="x", pady=(0, 15))
        
        self.gh_user_entry = ttk.Entry(gh_frame, width=30)
        self.gh_user_entry.insert(0, data.get("handle", ""))
        self.gh_user_entry.pack(side="left", padx=(0, 10))
        
        ttk.Button(gh_frame, text="⚡ Récupérer infos GitHub", command=self.fetch_github_profile).pack(side="left")

        ttk.Label(card, text="Nom affiché :", style="Card.TLabel").pack(anchor="w")
        self.p_user = ttk.Entry(card)
        self.p_user.insert(0, data.get("username", ""))
        self.p_user.pack(fill="x", pady=(0, 10))

        ttk.Label(card, text="URL Avatar :", style="Card.TLabel").pack(anchor="w")
        self.p_avatar = ttk.Entry(card)
        self.p_avatar.insert(0, data.get("avatar", ""))
        self.p_avatar.pack(fill="x", pady=(0, 10))

        ttk.Label(card, text="Bio :", style="Card.TLabel").pack(anchor="w")
        self.p_bio = ttk.Entry(card)
        self.p_bio.insert(0, data.get("bio", ""))
        self.p_bio.pack(fill="x", pady=(0, 15))

        ttk.Button(card, text="💾 Sauvegarder Profile.json", command=lambda: self.save_json("profile.json", {
            "username": self.p_user.get(),
            "handle": self.gh_user_entry.get(),
            "avatar": self.p_avatar.get(),
            "bio": self.p_bio.get(),
            "stats": data.get("stats", [])
        })).pack(anchor="e")

    def fetch_github_profile(self):
        username = self.gh_user_entry.get().strip()
        if not username: return
        try:
            url = f"https://api.github.com/users/{username}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                gh_data = json.loads(response.read().decode())
                self.p_user.delete(0, tk.END); self.p_user.insert(0, gh_data.get("name") or username)
                self.p_avatar.delete(0, tk.END); self.p_avatar.insert(0, gh_data.get("avatar_url", ""))
                self.p_bio.delete(0, tk.END); self.p_bio.insert(0, gh_data.get("bio") or "")
                messagebox.showinfo("Succès", "Informations GitHub récupérées !")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la récupération : {e}")

    # ==================== CATÉGORIES & SOUS-CATÉGORIES ====================
    def init_categories_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🗂️ Catégories")

        self.cat_tree = ttk.Treeview(tab, columns=("id", "parent", "name", "icon"), show="headings")
        self.cat_tree.heading("id", text="ID (Slug)")
        self.cat_tree.heading("parent", text="Catégorie Parente")
        self.cat_tree.heading("name", text="Nom de la catégorie")
        self.cat_tree.heading("icon", text="Icône FontAwesome ou URL")
        self.cat_tree.pack(fill="both", expand=True, padx=15, pady=10)

        self.cat_menu = tk.Menu(self.root, tearoff=0)
        self.cat_menu.add_command(label="✏️ Éditer", command=self.edit_cat)
        self.cat_menu.add_command(label="❌ Supprimer", command=self.del_cat)
        self.cat_tree.bind("<Button-3>", lambda e: self.show_tree_menu(e, self.cat_tree, self.cat_menu))

        card = ttk.Frame(tab, style="Card.TFrame", padding=10)
        card.pack(fill="x", padx=15, pady=(0, 10), side="bottom")

        ttk.Label(card, text="ID (Slug) :", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=5)
        self.c_id = ttk.Entry(card, width=12)
        self.c_id.grid(row=1, column=0, padx=5)

        ttk.Label(card, text="Parente (Sous-cat. de) :", style="Card.TLabel").grid(row=0, column=1, sticky="w", padx=5)
        self.c_parent = ttk.Combobox(card, width=15, state="readonly")
        self.c_parent.grid(row=1, column=1, padx=5)

        ttk.Label(card, text="Nom :", style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=5)
        self.c_name = ttk.Entry(card, width=20)
        self.c_name.grid(row=1, column=2, padx=5)

        ttk.Label(card, text="Icône FA ou URL Image :", style="Card.TLabel").grid(row=0, column=3, sticky="w", padx=5)
        self.c_icon = ttk.Entry(card, width=25)
        self.c_icon.insert(0, "fa-solid fa-folder")
        self.c_icon.grid(row=1, column=3, padx=5)

        ttk.Button(card, text="🎨 Pick", command=lambda: IconPickerPopup(self.root, self.c_icon)).grid(row=1, column=4, padx=2)
        ttk.Button(card, text="➕ Valider", command=self.add_cat).grid(row=1, column=5, padx=5)
        ttk.Button(card, text="💾 Sauvegarder JSON", command=lambda: self.save_json("categories.json", self.cat_data)).grid(row=1, column=6, padx=5)

        self.refresh_cats()

    def refresh_cats(self):
        for row in self.cat_tree.get_children():
            self.cat_tree.delete(row)
        
        parents = ["(Aucune - Principale)"]
        for c in self.cat_data:
            parent_display = c.get("parent", "") or "-"
            self.cat_tree.insert("", "end", values=(c.get("id"), parent_display, c.get("name"), c.get("icon")))
            if c["id"] != "all":
                parents.append(c["id"])

        self.c_parent["values"] = parents
        self.c_parent.current(0)

        if hasattr(self, 'left_cat_list'):
            self.refresh_left_cat_list()

    def add_cat(self):
        cid = self.c_id.get().strip()
        cname = self.c_name.get().strip()
        cicon = self.c_icon.get().strip()
        cparent = self.c_parent.get()
        if cparent == "(Aucune - Principale)" or not cparent:
            cparent = None

        if cid and cname:
            self.cat_data = [c for c in self.cat_data if c["id"] != cid]
            self.cat_data.append({"id": cid, "name": cname, "icon": cicon, "parent": cparent})
            self.refresh_cats()
            self.c_id.delete(0, tk.END); self.c_name.delete(0, tk.END)

    def edit_cat(self):
        selected = self.cat_tree.selection()
        if not selected: return
        item = self.cat_tree.item(selected[0])["values"]
        self.c_id.delete(0, tk.END); self.c_id.insert(0, item[0])
        self.c_name.delete(0, tk.END); self.c_name.insert(0, item[2])
        self.c_icon.delete(0, tk.END); self.c_icon.insert(0, item[3])
        
        p = item[1] if item[1] != "-" else "(Aucune - Principale)"
        if p in self.c_parent["values"]:
            self.c_parent.set(p)

    def del_cat(self):
        selected = self.cat_tree.selection()
        if not selected: return
        cid = self.cat_tree.item(selected[0])["values"][0]
        self.cat_data = [c for c in self.cat_data if c["id"] != cid]
        self.refresh_cats()

    # ==================== DÉPÔTS & PROJETS ====================
    def init_projects_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🚀 Dépôts & Projets")

        paned = ttk.PanedWindow(tab, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=5, pady=5)

        # GAUCHE : Menu Arborescent Catégories / Sous-catégories
        left_frame = ttk.Frame(paned, style="Card.TFrame", padding=10)
        paned.add(left_frame, weight=1)

        ttk.Label(left_frame, text="🗂️ Arborescence", style="Card.TLabel", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        self.cat_tree_view = ttk.Treeview(left_frame, show="tree", selectmode="browse")
        self.cat_tree_view.pack(fill="both", expand=True)
        self.cat_tree_view.bind("<<TreeviewSelect>>", self.on_category_tree_selected)

        # DROITE : Liste des Dépôts + Formulaire
        right_frame = ttk.Frame(paned, padding=5)
        paned.add(right_frame, weight=4)

        self.proj_tree = ttk.Treeview(right_frame, columns=("title", "github", "demo"), show="headings")
        self.proj_tree.heading("title", text="Nom du Dépôt (Double-clic pour Aperçu)")
        self.proj_tree.heading("github", text="Lien Dépôt GitHub")
        self.proj_tree.heading("demo", text="Lien Site Web")
        self.proj_tree.pack(fill="both", expand=True, pady=(0, 5))

        # Double-clic pour ouvrir l'aperçu
        self.proj_tree.bind("<Double-1>", self.open_project_preview)

        self.proj_menu = tk.Menu(self.root, tearoff=0)
        self.proj_menu.add_command(label="👁️ Prévisualiser (Stars, README...)", command=self.open_project_preview)
        self.proj_menu.add_command(label="✏️ Éditer ce dépôt", command=self.edit_proj)
        self.proj_menu.add_command(label="❌ Supprimer ce dépôt", command=self.del_proj)
        self.proj_tree.bind("<Button-3>", lambda e: self.show_tree_menu(e, self.proj_tree, self.proj_menu))

        # Formulaire compact
        card = ttk.Frame(right_frame, style="Card.TFrame", padding=10)
        card.pack(fill="x", side="bottom")

        r1 = ttk.Frame(card, style="Card.TFrame")
        r1.pack(fill="x", pady=2)
        ttk.Label(r1, text="Titre :", style="Card.TLabel").pack(side="left")
        self.pj_title = ttk.Entry(r1, width=20); self.pj_title.pack(side="left", padx=(5, 15))
        ttk.Label(r1, text="GitHub :", style="Card.TLabel").pack(side="left")
        self.pj_github = ttk.Entry(r1); self.pj_github.pack(side="left", fill="x", expand=True, padx=(5, 15))
        ttk.Label(r1, text="Site Web :", style="Card.TLabel").pack(side="left")
        self.pj_demo = ttk.Entry(r1); self.pj_demo.pack(side="left", fill="x", expand=True)

        r2 = ttk.Frame(card, style="Card.TFrame")
        r2.pack(fill="x", pady=2)
        ttk.Label(r2, text="Description :", style="Card.TLabel").pack(side="left")
        self.pj_desc = ttk.Entry(r2); self.pj_desc.pack(side="left", fill="x", expand=True, padx=(5, 15))
        ttk.Label(r2, text="Images (URLs) :", style="Card.TLabel").pack(side="left")
        self.pj_imgs = ttk.Entry(r2, width=20); self.pj_imgs.pack(side="left", padx=(5, 15))
        ttk.Label(r2, text="Tags :", style="Card.TLabel").pack(side="left")
        self.pj_tags = ttk.Entry(r2, width=20); self.pj_tags.pack(side="left")

        r3 = ttk.Frame(card, style="Card.TFrame")
        r3.pack(fill="x", pady=(8, 0))
        ttk.Button(r3, text="➕ Enregistrer le Dépôt", command=self.add_proj).pack(side="right", padx=5)
        ttk.Button(r3, text="💾 Sauvegarder Projects.json", command=lambda: self.save_json("projects.json", self.proj_data)).pack(side="right", padx=5)

        self.refresh_left_cat_list()

    def refresh_left_cat_list(self):
        for item in self.cat_tree_view.get_children():
            self.cat_tree_view.delete(item)

        # Insérer les catégories principales
        mains = [c for c in self.cat_data if not c.get("parent") and c["id"] != "all"]
        for m in mains:
            parent_node = self.cat_tree_view.insert("", "end", iid=m["id"], text=f"📂 {m['name']}")
            # Insérer les sous-catégories rattachées
            subs = [c for c in self.cat_data if c.get("parent") == m["id"]]
            for s in subs:
                self.cat_tree_view.insert(parent_node, "end", iid=s["id"], text=f"  └─ {s['name']}")

    def get_selected_cat_id(self):
        sel = self.cat_tree_view.selection()
        return sel[0] if sel else None

    def on_category_tree_selected(self, event):
        self.refresh_filtered_projs()
        self.clear_proj_form()

    def refresh_filtered_projs(self):
        cat_id = self.get_selected_cat_id()
        for row in self.proj_tree.get_children():
            self.proj_tree.delete(row)

        if not cat_id: return

        filtered = [p for p in self.proj_data if p.get("category") == cat_id]
        for p in filtered:
            self.proj_tree.insert("", "end", values=(p.get("title"), p.get("github"), p.get("demo")))

    def open_project_preview(self, event=None):
        selected = self.proj_tree.selection()
        if not selected: return
        title = self.proj_tree.item(selected[0])["values"][0]
        p = next((x for x in self.proj_data if x["title"] == title), None)
        if p:
            ProjectPreviewPopup(self.root, p)

    def add_proj(self):
        cat_id = self.get_selected_cat_id()
        if not cat_id:
            messagebox.showwarning("Attention", "Sélectionne une catégorie à gauche.")
            return

        title = self.pj_title.get().strip()
        if not title: return

        imgs = [i.strip() for i in self.pj_imgs.get().split(",") if i.strip()]
        tags = [t.strip() for t in self.pj_tags.get().split(",") if t.strip()]

        self.proj_data = [p for p in self.proj_data if p["title"].lower() != title.lower()]
        self.proj_data.append({
            "id": title.lower().replace(" ", "-"),
            "title": title,
            "category": cat_id,
            "description": self.pj_desc.get(),
            "images": imgs,
            "github": self.pj_github.get(),
            "demo": self.pj_demo.get(),
            "tags": tags
        })
        self.refresh_filtered_projs()
        self.clear_proj_form()

    def edit_proj(self):
        selected = self.proj_tree.selection()
        if not selected: return
        title = self.proj_tree.item(selected[0])["values"][0]
        p = next((x for x in self.proj_data if x["title"] == title), None)
        if not p: return

        self.pj_title.delete(0, tk.END); self.pj_title.insert(0, p.get("title", ""))
        self.pj_desc.delete(0, tk.END); self.pj_desc.insert(0, p.get("description", ""))
        self.pj_imgs.delete(0, tk.END); self.pj_imgs.insert(0, ", ".join(p.get("images", [])))
        self.pj_github.delete(0, tk.END); self.pj_github.insert(0, p.get("github", ""))
        self.pj_demo.delete(0, tk.END); self.pj_demo.insert(0, p.get("demo", ""))
        self.pj_tags.delete(0, tk.END); self.pj_tags.insert(0, ", ".join(p.get("tags", [])))

    def del_proj(self):
        selected = self.proj_tree.selection()
        if not selected: return
        title = self.proj_tree.item(selected[0])["values"][0]
        self.proj_data = [p for p in self.proj_data if p["title"] != title]
        self.refresh_filtered_projs()

    def clear_proj_form(self):
        for e in (self.pj_title, self.pj_desc, self.pj_imgs, self.pj_github, self.pj_demo, self.pj_tags):
            e.delete(0, tk.END)

    # ==================== RÉSEAUX (ÉDITION COMPLETE ET SELECTEUR D'ICÔNE) ====================
    def init_socials_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🌐 Réseaux")

        self.soc_tree = ttk.Treeview(tab, columns=("name", "url", "icon"), show="headings")
        self.soc_tree.heading("name", text="Réseau")
        self.soc_tree.heading("url", text="Lien")
        self.soc_tree.heading("icon", text="Icône FontAwesome ou URL")
        self.soc_tree.pack(fill="both", expand=True, padx=15, pady=10)

        self.soc_menu = tk.Menu(self.root, tearoff=0)
        self.soc_menu.add_command(label="✏️ Éditer", command=self.edit_social)
        self.soc_menu.add_command(label="❌ Supprimer", command=self.del_social)
        self.soc_tree.bind("<Button-3>", lambda e: self.show_tree_menu(e, self.soc_tree, self.soc_menu))

        card = ttk.Frame(tab, style="Card.TFrame", padding=10)
        card.pack(fill="x", padx=15, pady=(0, 10), side="bottom")

        ttk.Label(card, text="Nom :", style="Card.TLabel").grid(row=0, column=0, sticky="w", padx=5)
        self.s_name = ttk.Entry(card, width=15); self.s_name.grid(row=1, column=0, padx=5)

        ttk.Label(card, text="URL :", style="Card.TLabel").grid(row=0, column=1, sticky="w", padx=5)
        self.s_url = ttk.Entry(card, width=35); self.s_url.grid(row=1, column=1, padx=5)

        ttk.Label(card, text="Icône FA ou URL Image :", style="Card.TLabel").grid(row=0, column=2, sticky="w", padx=5)
        self.s_icon = ttk.Entry(card, width=25); self.s_icon.insert(0, "fa-brands fa-github"); self.s_icon.grid(row=1, column=2, padx=5)

        ttk.Button(card, text="🎨 Pick", command=lambda: IconPickerPopup(self.root, self.s_icon)).grid(row=1, column=3, padx=2)
        ttk.Button(card, text="➕ Valider", command=self.add_social).grid(row=1, column=4, padx=5)
        ttk.Button(card, text="💾 Sauvegarder JSON", command=lambda: self.save_json("socials.json", self.socials_data)).grid(row=1, column=5, padx=5)

        self.refresh_socials()

    def refresh_socials(self):
        for row in self.soc_tree.get_children():
            self.soc_tree.delete(row)
        for s in self.socials_data:
            self.soc_tree.insert("", "end", values=(s.get("name"), s.get("url"), s.get("icon")))

    def add_social(self):
        name = self.s_name.get().strip()
        if name:
            self.socials_data = [s for s in self.socials_data if s["name"].lower() != name.lower()]
            self.socials_data.append({"name": name, "url": self.s_url.get().strip(), "icon": self.s_icon.get().strip()})
            self.refresh_socials()
            self.s_name.delete(0, tk.END); self.s_url.delete(0, tk.END)

    def edit_social(self):
        selected = self.soc_tree.selection()
        if not selected: return
        item = self.soc_tree.item(selected[0])["values"]
        self.s_name.delete(0, tk.END); self.s_name.insert(0, item[0])
        self.s_url.delete(0, tk.END); self.s_url.insert(0, item[1])
        self.s_icon.delete(0, tk.END); self.s_icon.insert(0, item[2])

    def del_social(self):
        selected = self.soc_tree.selection()
        if not selected: return
        name = self.soc_tree.item(selected[0])["values"][0]
        self.socials_data = [s for s in self.socials_data if s["name"] != name]
        self.refresh_socials()

    def show_tree_menu(self, event, tree, menu):
        item = tree.identify_row(event.y)
        if item:
            tree.selection_set(item)
            menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    root = tk.Tk()
    app = NexgenStudio(root)
    root.mainloop()