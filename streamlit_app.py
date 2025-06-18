import streamlit as st
import pandas as pd
import json # Kept for loading local config for bcrypt, but data handling moves to GSheets
from datetime import datetime, date, time
import uuid
import altair as alt
import pathlib
import yaml
from yaml.loader import SafeLoader
import bcrypt
import gspread
from google.oauth2 import service_account

# --- Google Sheets Configuration ---
# These will be loaded from st.secrets
# SPREADSHEET_URLS = {
#     "records": "YOUR_RECORDS_GOOGLE_SHEET_URL",
#     "user_profiles": "YOUR_USER_PROFILES_GOOGLE_SHEET_URL",
#     "training_log": "YOUR_TRAINING_LOG_GOOGLE_SHEET_URL",
#     "instructor_feedback": "YOUR_INSTRUCTOR_FEEDBACK_GOOGLE_SHEET_URL",
# }

# --- Privileged User Configuration ---
PRIVILEGED_USERS = ["Philippe K.", "Vincent C.", "Charles D.B.", "Rémy L.", "Gregory D."]
SUPER_PRIVILEGED_USERS = ['Charles D.B.']

# Instructor certification levels for different functionalities
INSTRUCTOR_CERT_LEVELS_FOR_LOGGING_FEEDBACK_SIDEBAR = ["S4", "I1", "I2", "I3"]
INSTRUCTOR_CERT_LEVELS_FOR_ADMIN_TABS_AND_DROPDOWNS = ["A3", "S4", "I1", "I2", "I3"]

# --- Discipline Configuration ---
LOWER_IS_BETTER_DISCIPLINES = ["16x25m Speed Endurance"]

# --- Styling ---
FEEDBACK_TAG_COLORS = {
    "#apnée/marche": "#4CAF50",         # Green
    "#apnée/stretching": "#2196F3",     # Blue
    "#apnée/statique": "#FFC107",       # Amber
    "#apnée/dynamique": "#f44336",      # Red
    "#apnée/respiration": "#2196F3",    # Blue
    "#apnée/profondeur": "#9C27B0",     # Violet (Purple)
}

# --- Language Translations ---
TRANSLATIONS = {
    "fr": {
        "page_title": "MacaJournal",
        "app_title": "🌊 Mon Journal Macapnée",
        "user_management_header": "👤 Gestion des Apnéistes",
        "no_users_yet": "Aucun apnéiste pour le moment. Ajoutez-en un via l'onglet Apnéistes.",
        "enter_freediver_name_sidebar": "Entrez le nom du Nouvel Apnéiste (Format: Prénom L.)",
        "confirm_freediver_button_sidebar": "Afficher les Données",
        "new_user_success": "Nouvel apnéiste : **{user}**. Profil/performance à sauvegarder pour finaliser.",
        "select_user_or_add": "Sélectionnez un apnéiste",
        "add_new_user_option": "✨ Ajouter un nouvel apnéiste...",
        "existing_user_selected": "Apnéiste **{user}** confirmé.",
        "log_performance_header": "✏️ Nouvelle Performance",
        "profile_header_sidebar": "👤 Profil Apnéiste",
        "select_user_first_warning": "Connectez-vous pour enregistrer des performances.",
        "logging_for": "Enregistrement pour : **{user}**",
        "link_training_session_label": "Activité",
        "no_specific_session_option": "Événement personnalisé / Aucune session spécifique",
        "entry_date_label": "Date d'Entrée",
        "discipline": "Discipline",
        "performance_value": "Valeur de la performance",
        "sta_help": "Format : MM:SS (ex: 03:45). Les millisecondes seront ignorées à l'affichage.",
        "dyn_depth_help": "Format : Nombre, optionnellement suivi de 'm' (ex: 75 ou 75m)",
        "save_performance_button": "💾 Enregistrer la performance",
        "performance_value_empty_error": "La valeur de la performance ne peut pas être vide.",
        "event_name_empty_error": "Le nom de l'événement ne peut pas être vide (si aucune session d'entraînement n'est liée).",
        "performance_saved_success": "Performance enregistrée pour {user} !",
        "process_performance_error": "Échec du traitement de la valeur de performance. Veuillez vérifier le format.",
        "my_performances_header": "📬 Mes Performances ({user})",
        "personal_records_tab_label": "📊 Mes Performances",
        "select_user_to_view_personal_records": "Veuillez vous connecter pour voir vos records personnels.",
        "no_performances_yet": "Aucune performance enregistrée pour cet apnéiste. Ajoutez-en via la barre latérale !",
        "personal_bests_subheader": "🌟 Records Personnels",
        "club_bests_subheader": "🏆 Meilleures Performances du Club",
        "pb_labels": {
            "Dynamic Bi-fins (DYN-BF)": "Record DYNB",
            "Static Apnea (STA)": "Record STA",
            "Dynamic No-fins (DNF)": "Record DNF",
            "Depth (CWT/FIM)": "Record CWT/FIM",
            "Depth (VWT/NLT)": "Record VWT/NLT",
            "16x25m Speed Endurance": "Record 16x25m"
        },
        "club_best_labels": {
            "Dynamic Bi-fins (DYN-BF)": "Record Club DYNB",
            "Static Apnea (STA)": "Record Club STA",
            "Dynamic No-fins (DNF)": "Record Club DNF",
            "Depth (CWT/FIM)": "Record Club CWT/FIM",
            "Depth (VWT/NLT)": "Record Club VWT/NLT",
            "16x25m Speed Endurance": "Record Club 16x25m"
        },
        "achieved_at_event_on_date_caption": "Par {user} à {event_name} le {event_date}",
        "achieved_on_event_caption": "{event_name}, {event_date}",
        "no_record_yet_caption": "Aucun record pour l'instant",
        "performance_evolution_subheader": "📈 Évolution des Performances",
        "seconds_unit": "secondes",
        "meters_unit": "mètres",
        "minutes_unit": "minutes",
        "history_table_subheader": "📜 Tableau de l'Historique (Modifiable)",
        "full_history_subheader": "📜 Historique Complet",
        "history_event_name_col": "Nom Événement",
        "history_event_date_col": "Date Événement",
        "history_entry_date_col": "Date Entrée",
        "history_discipline_col": "Discipline",
        "history_performance_col": "Performance",
        "history_actions_col": "Actions",
        "history_delete_col_editor": "Supprimer ?",
        "no_history_display": "Aucun historique à afficher pour cette discipline.",
        "no_data_for_graph": "Aucune donnée à afficher pour le graphique de cette discipline.",
        "welcome_message": "👋 Bienvenue sur le Suivi d'Apnée ! Veuillez vous connecter pour commencer.",
        "select_user_prompt": "Veuillez vous connecter pour voir et enregistrer les performances.",
        "language_select_label": "🌐 Langue",
        "invalid_time_format": "Format de temps invalide '{time_str}'. Attendu MM:SS ou MM:SS.ms",
        "invalid_ms_format": "Format des millisecondes invalide dans '{time_str}'.",
        "time_values_out_of_range": "Valeurs de temps hors limites dans '{time_str}'.",
        "could_not_parse_time": "Impossible d'analyser la chaîne de temps '{time_str}'. Assurez-vous que les nombres sont corrects.",
        "distance_empty_error": "La valeur de distance ne peut pas être vide.",
        "distance_negative_error": "La distance ne peut pas être négative.",
        "invalid_distance_format": "Format de distance invalide '{dist_str}'. Utilisez un nombre, optionnellement suivi de 'm'.",
        "consent_ai_feedback_label": "Je consens à la génération de mon feedback par une IA",
        "consent_ai_feedback_missing": "Veuillez donner votre consentement dans la section 'Profil Apnéiste' de la barre latérale pour activer la génération de feedback par l'IA.",
        "disciplines": {
            "Static Apnea (STA)": "Apnée Statique (STA)",
            "Dynamic Bi-fins (DYN-BF)": "Dynamique Bi-palmes (DYN-BF)",
            "Dynamic No-fins (DNF)": "Dynamique Sans Palmes (DNF)",
            "Depth (CWT/FIM)": "Profondeur (CWT/FIM)",
            "Depth (VWT/NLT)": "Profondeur (VWT/NLT)",
            "16x25m Speed Endurance": "16x25m Vitesse Endurance"
        },
        "months": {
            "January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin",
            "July": "Juillet", "August": "Août", "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"
        },
        "performances_main_tab_title": "📊 Performances",
        "club_performances_overview_tab_label": "🏆 Classement [A]",
        "select_discipline_for_ranking": "Sélectionnez la discipline pour le classement :",
        "podium_header": "🏆 Podium",
        "full_ranking_header": "📋 Classement Complet",
        "rank_col": "Rang",
        "user_col": "Apnéiste",
        "best_performance_col": "Meilleure Performance",
        "event_col": "Événement",
        "date_achieved_col": "Date Événement",
        "no_ranking_data": "Aucune donnée de classement disponible pour cette discipline pour le moment.",
        "profile_tab_title": "🪪 Profil Apnéiste",
        "certification_label": "Niveau de Brevet :",
        "certification_date_label": "Date du Brevet :",
        "lifras_id_label": "ID LIFRAS :",
        "anonymize_results_label": "Anonymiser mes résultats",
        "anonymize_results_col_editor": "Anonymiser ?",
        "anonymous_freediver_name": "Apnéiste Anonyme",
        "save_profile_button": "💾 Enregistrer le Profil",
        "profile_saved_success": "Profil enregistré avec succès pour {user} !",
        "select_user_to_edit_profile": "Connectez-vous pour voir ou modifier votre profil.",
        "no_certification_option": "Non Spécifié",
        "certification_levels": {
            "A1": "A1", "A2": "A2", "A3": "A3", "S4": "S4",
            "I1": "I1", "I2": "I2", "I3": "I3", "NB": "NB"
        },
        "certification_stats_header": "📊 Statistiques par Niveau de Brevet",
        "certification_level_col": "Niveau de Brevet",
        "min_performance_col": "Perf. Min",
        "max_performance_col": "Perf. Max",
        "avg_performance_col": "Perf. Moyenne",
        "no_stats_data": "Aucune donnée disponible pour les statistiques par brevet dans cette discipline.",
        "edit_action": "Modifier",
        "delete_action": "Supprimer",
        "edit_performance_header": "✏️ Modifier la Performance",
        "save_changes_button": "💾 Enregistrer les Modifications",
        "save_history_changes_button": "💾 Sauvegarder l'Historique",
        "cancel_edit_button": "❌ Annuler la Modification",
        "confirm_delete_button": "🗑️ Confirmer la Suppression",
        "delete_confirmation_prompt": "Êtes-vous sûr de vouloir supprimer cette performance : {event_date} à {event_name} - {performance} ?",
        "performance_deleted_success": "Performance supprimée avec succès.",
        "no_record_found_for_editing": "Erreur : Impossible de trouver l'enregistrement à modifier.",
        "performance_updated_success": "Performance mise à jour avec succès.",
        "history_updated_success": "Historique mis à jour avec succès.",
        "critical_error_edit_id_not_found": "Erreur critique : ID d'enregistrement '{record_id}' à modifier non trouvé dans la liste principale. Modification annulée.",
        "club_performances_tab_title": "📈 Performances du Club",
        "club_level_performance_tab_title": "🏆 Performances du Club",
        "no_data_for_club_performance_display": "Aucune donnée de performance disponible pour le club dans cette discipline.",
        "quarterly_average_label": "Moyenne Trimestrielle",
        "freedivers_tab_title": "🫂 Apnéistes [A]",
        "edit_freedivers_header": "🫂 Gérer les Apnéistes",
        "freediver_name_col_editor": "Nom Apnéiste (Prénom L.)",
        "set_reset_password_col_editor": "Définir/Réinitialiser Mot de Passe",
        "set_reset_password_help": "Entrez un nouveau mot de passe pour le définir ou le réinitialiser. Laissez vide pour conserver le mot de passe actuel.",
        "certification_col_editor": "Niveau de Brevet",
        "certification_date_col_editor": "Date Brevet",
        "lifras_id_col_editor": "ID LIFRAS",
        "pb_sta_col_editor": "PB STA",
        "pb_dynbf_col_editor": "PB DYN-BF",
        "pb_dnf_col_editor": "PB DNF",
        "pb_depth_col_editor": "PB Prof. (CWT/FIM)",
        "pb_vwt_nlt_col_editor": "PB Prof. (VWT/NLT)",
        "pb_16x25_col_editor": "PB 16x25m",
        "save_freedivers_changes_button": "💾 Sauvegarder les Modifications des Apnéistes",
        "freedivers_updated_success": "Données des apnéistes mises à jour avec succès.",
        "freediver_name_conflict_error": "Erreur : Le nom '{new_name}' est déjà utilisé par un autre apnéiste. Veuillez choisir un nom unique.",
        "original_name_col_editor_hidden": "nom_original",
        "freediver_certification_summary_header": "🔢 Apnéistes par Niveau de Brevet",
        "count_col": "Nombre",
        "training_log_tab_title": "📅 Activités",
        "log_training_header_sidebar": "🏋️ Nouvelle Activité",
        "training_date_label": "Date de l'Activité",
        "training_place_label": "Lieu",
        "training_description_label": "Description",
        "save_training_button": "💾 Enregistrer l'Activité",
        "training_session_saved_success": "Activité enregistrée !",
        "training_description_empty_error": "La description de l'activité ne peut pas être vide.",
        "training_log_table_header": "📋 Activités (Modifiable)",
        "save_training_log_changes_button": "💾 Sauvegarder l'Activité",
        "training_log_updated_success": "Activité mise à jour avec succès.",
        "performances_overview_tab_label": "📅 Journal des Performances [A]",
        "edit_performances_sub_tab_label": "📝 Editer les Performances [A]",
        "save_all_performances_button": "💾 Sauvegarder les Modifications du Journal",
        "all_performances_updated_success": "Journal des performances mis à jour avec succès.",
        "feedback_log_tab_label": "💬 Feedbacks",
        "my_feedback_tab_label": "💬 Mon Feedback",
        "generate_feedback_summary_button": "Générer le résumé des feedbacks",
        "feedback_summary_header": "Résumé des feedbacks",
        "no_feedback_to_summarize": "Aucun feedback à résumer pour le moment.",
        "feedbacks_overview_tab_label": "💬 Journal des Feedbacks [A]",
        "edit_feedbacks_sub_tab_label": "📝 Editer les Feedbacks [A]",
        "log_feedback_header_sidebar": "📝 Feedback Instructeur",
        "feedback_for_freediver_label": "Apnéiste :",
        "feedback_log_tab_title" : "💬 Feedbacks",
        "training_session_label": "Activité Liée :",
        "instructor_name_label": "Instructeur :",
        "feedback_text_label": "Feedback :",
        "save_feedback_button": "💾 Enregistrer Feedback",
        "feedback_saved_success": "Feedback enregistré avec succès !",
        "feedback_text_empty_error": "Le texte du feedback ne peut pas être vide.",
        "feedback_log_table_header": "📋 Journal des Feedbacks (Modifiable)",
        "save_feedback_log_changes_button": "💾 Sauvegarder Modifs. Journal Feedback",
        "feedback_log_updated_success": "Journal des feedbacks mis à jour.",
        "no_feedback_for_user": "Aucun feedback reçu pour l'instant.",
        "no_feedback_in_log": "Aucun feedback enregistré dans le système.",
        "feedback_date_col": "Date Feedback",
        "select_training_prompt": "Sélectionnez une session (optionnel)",
        "select_freediver_prompt": "Sélectionnez l'Apnéiste",
        "select_instructor_prompt": "Sélectionnez l'Instructeur",
        "detailed_training_sessions_subheader": "Activités",
        "training_sessions_sub_tab_label": "🗓️ Journal d'Activités",
        "edit_training_sessions_sub_tab_label": "✏️ Editer les Activités [A]",
        "no_description_available": "Aucune description disponible.",
        "no_training_sessions_logged": "Aucune activité enregistrée pour le moment.",
        "filter_by_freediver_label": "Filtrer par Apnéiste :",
        "filter_by_training_session_label": "Filtrer par Activité :",
        "filter_by_instructor_label": "Filtrer par Instructeur :",
        "filter_by_discipline_label": "Filtrer par Discipline :",
        "all_freedivers_option": "Tous les Apnéistes",
        "all_sessions_option": "Toutes les Sessions",
        "all_instructors_option": "Tous les Instructeurs",
        "all_disciplines_option": "Toutes les Disciplines",
        "filter_by_year_label": "Filtrer par Année :",
        "filter_by_month_label": "Filtrer par Mois :",
        "filter_by_place_label": "Filtrer par Lieu :",
        "filter_by_tag_label": "Filtrer par Tag",
        "all_tags_option": "Tous les Tags",
        "all_years_option": "Toutes les Années",
        "all_months_option": "Tous les Mois",
        "all_places_option": "Tous les Lieux",
        "no_feedbacks_match_filters": "Aucun feedback ne correspond aux filtres actuels.",
        "login_error": "Nom d'utilisateur ou mot de passe incorrect.",
        "login_welcome": "Veuillez vous connecter pour continuer.",
        "logout_button": "Déconnexion"
    }
}

# --- Helper to get translated text ---
def _(key, lang='fr', **kwargs):
    """
    Gets a translated string for the given key.
    Since only French is available, it always uses the 'fr' dictionary.
    """
    # The lang parameter is kept for compatibility but is ignored.
    keys = key.split('.')
    translation_set = TRANSLATIONS['fr']  # Directly access French translations

    value = translation_set
    try:
        for k_loop in keys:
            value = value[k_loop]
        if kwargs:
            return value.format(**kwargs)
        return value
    except KeyError:
        # Fallback to the key itself if not found in French translations
        return key

# --- Helper for anonymization ---
def get_display_name(user_name, user_profiles, lang):
    if user_name and user_name in user_profiles:
        if user_profiles[user_name].get("anonymize_results", False):
            return _("anonymous_freediver_name", lang)
    return user_name

# --- Google Sheets Connection ---
@st.cache_resource(ttl=3600) # Cache the connection for an hour
def get_gsheets_client():
    try:
        # Use st.secrets to get credentials for service account
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gsheets"],
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        st.info("Please ensure your `.streamlit/secrets.toml` is correctly configured and Google Sheets/Drive APIs are enabled for your service account.")
        st.stop()
        return None

def get_sheet_by_url(client, url, worksheet_name='Sheet1'): # Added worksheet_name parameter
    try:
        spreadsheet = client.open_by_url(url)
        # Assuming your data is in the first worksheet or a worksheet named 'Sheet1'
        # You might need to adjust 'Sheet1' to the actual name of your worksheet
        return spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Worksheet '{worksheet_name}' not found in the Google Sheet at {url}. Please check the worksheet name.")
        st.stop()
        return None
    except Exception as e:
        st.error(f"Error opening Google Sheet with URL {url}: {e}")
        st.stop()
        return None

# --- Data Handling for Performance Records ---
@st.cache_data(ttl=60) # Cache data for 60 seconds
def load_records(training_logs):
    client = get_gsheets_client()
    # Pass the specific worksheet name for records
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["records_sheet_url"], 'freediving_records') # <-- Change 'Sheet1' to your actual worksheet name for records
    records = sheet.get_all_records()
    
    # Ensure IDs and perform migrations if necessary
    updated = False
    for record in records:
        if record.get('id') is None:
            record['id'] = uuid.uuid4().hex
            updated = True
        if 'entry_date' not in record:
            record['entry_date'] = date.today().isoformat()
            updated = True
        if 'linked_training_session_id' not in record:
            record['linked_training_session_id'] = None
            updated = True
            
        # Clean up old fields if linked_training_session_id exists and is valid
        if record.get('linked_training_session_id') in {log['id'] for log in training_logs}:
            if 'event_name' in record:
                del record['event_name']
                updated = True
            if 'event_date' in record:
                del record['event_date']
                updated = True
            if 'date' in record: # Very old versions
                del record['date']
                updated = True

    if updated:
        save_records(records) # Save after migration
    return records

def save_records(records):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["records_sheet_url"], 'freediving_records') # <-- Change 'Sheet1'
    
    # Prepare data for saving - ensure all records have consistent keys for headers
    # This is important for gspread to update correctly.
    if not records:
        # Clear sheet if no records are left
        sheet.clear()
        # Add header row if desired, e.g., sheet.append_row(list(initial_record_keys))
        return
    
    # Get all column headers from the first record (assume consistent schema)
    # Or define a strict schema if you prefer
    headers = list(records[0].keys())
    data_to_write = [headers] + [[record.get(h) for h in headers] for record in records]
    
    # Clear existing content and write all data back
    sheet.clear()
    sheet.update(data_to_write)
    load_records.clear() # Clear cache after saving

# --- Data Handling for User Profiles ---
@st.cache_data(ttl=60)
def load_user_profiles():
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["user_profiles_sheet_url"], 'user_profiles') # <-- Change 'Sheet1'
    # Get all records as a list of dictionaries
    profiles_list = sheet.get_all_records()
    # Convert list of dicts to the dictionary format expected by the app {username: profile_data}
    profiles = {p['user_name']: p for p in profiles_list if 'user_name' in p}
    
    # Ensure 'user_name' column exists in the sheet. If not, add a migration.
    # For initial setup, it's simpler to manually create the sheet with the expected header.
    # Also, ensure all existing users have an 'id' for authentication later.
    updated = False
    for user_name, profile_data in profiles.items():
        if profile_data.get('id') is None:
            profile_data['id'] = uuid.uuid4().hex
            updated = True
    
    if updated:
        save_user_profiles(profiles) # Save after migration
    return profiles

def save_user_profiles(profiles):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["user_profiles_sheet_url"], 'user_profiles') # <-- Change 'Sheet1'
    
    profiles_list = list(profiles.values())
    if not profiles_list:
        sheet.clear()
        return

    # Ensure 'user_name' is a consistent key for all profiles
    for name, profile in profiles.items():
        profile['user_name'] = name # Ensure the key used for the dict is stored as a column
    
    headers = list(profiles_list[0].keys())
    data_to_write = [headers] + [[profile.get(h) for h in headers] for profile in profiles_list]
    
    sheet.clear()
    sheet.update(data_to_write)
    load_user_profiles.clear() # Clear cache after saving

# --- Data Handling for Training Logs ---
@st.cache_data(ttl=60)
def load_training_log():
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["training_log_sheet_url"], 'training_log') # <-- Change 'Sheet1'
    logs = sheet.get_all_records()
    
    updated = False
    for entry in logs:
        if entry.get('id') is None:
            entry['id'] = uuid.uuid4().hex
            updated = True
    
    if updated:
        save_training_log(logs) # Save after migration
    return logs

def save_training_log(logs):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["training_log_sheet_url"], 'training_log') # <-- Change 'Sheet1'
    
    if not logs:
        sheet.clear()
        return
    
    headers = list(logs[0].keys())
    data_to_write = [headers] + [[log.get(h) for h in headers] for log in logs]
    
    sheet.clear()
    sheet.update(data_to_write)
    load_training_log.clear() # Clear cache after saving

# --- Data Handling for Instructor Feedback ---
@st.cache_data(ttl=60)
def load_instructor_feedback():
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["instructor_feedback_sheet_url"], 'instructor_feedback') # <-- Change 'Sheet1'
    feedback_data = sheet.get_all_records()
    
    updated = False
    for entry in feedback_data:
        if entry.get('id') is None:
            entry['id'] = uuid.uuid4().hex
            updated = True
    
    if updated:
        save_instructor_feedback(feedback_data) # Save after migration
    return feedback_data

def save_instructor_feedback(feedback_data):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["instructor_feedback_sheet_url"], 'instructor_feedback') # <-- Change 'Sheet1'
    
    if not feedback_data:
        sheet.clear()
        return
    
    headers = list(feedback_data[0].keys())
    data_to_write = [headers] + [[fb.get(h) for h in headers] for fb in feedback_data]
    
    sheet.clear()
    sheet.update(data_to_write)
    load_instructor_feedback.clear() # Clear cache after saving

# --- Authentication Config Handling ---
@st.cache_data(ttl=300)
def get_auth_config():
    """
    Loads authenticator config. Since user profiles are now in GSheets,
    this function will generate credentials based on GSheets data.
    """
    profiles = load_user_profiles() # Load profiles from GSheets
    training_logs = load_training_log() # Need training logs for load_records migration
    all_records = load_records(training_logs) # Load records to get all users

    all_users = sorted(list(set(r['user'] for r in all_records).union(set(profiles.keys()))))
    
    credentials = {'usernames': {}}
    
    for user_name in all_users:
        user_profile = profiles.get(user_name, {})
        
        # --- FIX START ---
        # Ensure lifras_id is a string before stripping
        lifras_id = str(user_profile.get("lifras_id", "")).strip()
        # --- FIX END ---

        plain_password = lifras_id if lifras_id else "changeme"
        
        password_bytes = plain_password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
        
        username_key = ''.join(filter(str.isalnum, user_name)).lower()
        credentials['usernames'][username_key] = {
            "email": f"{username_key}@example.com",
            "name": user_name,
            "password": hashed_password_bytes.decode('utf-8')
        }

    config = {
        'credentials': credentials,
        'cookie': {'name': 'freediving_cookie', 'key': 'a_secret_key', 'expiry_days': 30}
    }
    
    return config

def verify_password(plain_password, hashed_password):
    """Verifies a plain password against a hashed one."""
    plain_password_bytes = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)

# --- Performance Parsing and Formatting ---
def is_time_based_discipline(discipline_key):
    return discipline_key in ["Static Apnea (STA)", "16x25m Speed Endurance"]

def is_lower_better(discipline_key):
    return discipline_key in LOWER_IS_BETTER_DISCIPLINES

def parse_static_time_to_seconds(time_str, lang='fr'):
    try:
        parts = str(time_str).split(':')
        if len(parts) != 2: st.error(_("invalid_time_format", lang, time_str=time_str)); return None
        minutes = int(parts[0])
        sec_ms_part = parts[1]
        if '.' in sec_ms_part:
            sec_parts = sec_ms_part.split('.')
            if len(sec_parts) != 2: st.error(_("invalid_ms_format", lang, time_str=time_str)); return None
            seconds = int(sec_parts[0]); milliseconds_str = sec_parts[1][:3].ljust(3, '0'); milliseconds = int(milliseconds_str)
            total_seconds = minutes * 60 + seconds + milliseconds / 1000.0
        else:
            seconds = int(sec_ms_part); total_seconds = float(minutes * 60 + seconds)
        if not (0 <= minutes and 0 <= seconds < 60 and (0 <= milliseconds < 1000 if '.' in sec_ms_part else True)):
            st.error(_("time_values_out_of_range", lang, time_str=time_str)); return None
        return total_seconds
    except (ValueError, TypeError): st.error(_("could_not_parse_time", lang, time_str=time_str)); return None

def format_seconds_to_static_time(total_seconds_float):
    if total_seconds_float is None or pd.isna(total_seconds_float): return "N/A"
    total_seconds_float = float(total_seconds_float); rounded_total_seconds = round(total_seconds_float)
    minutes = int(rounded_total_seconds // 60); seconds = int(rounded_total_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def parse_distance_to_meters(dist_str, lang='fr'):
    try:
        cleaned_dist_str = str(dist_str).lower().replace('m', '').strip()
        if not cleaned_dist_str: st.error(_("distance_empty_error", lang)); return None
        val = int(cleaned_dist_str)
        if val < 0: st.error(_("distance_negative_error", lang)); return None
        return val
    except (ValueError, TypeError): st.error(_("invalid_distance_format", lang, dist_str=dist_str)); return None

# --- Helper to get session details ---
def get_training_session_details(session_id, training_logs):
    """Fetches training session details by ID."""
    if not session_id:
        return {"event_date": None, "event_name": _("no_specific_session_option")}
    for log in training_logs:
        if log.get('id') == session_id:
            return {
                "event_date": log.get('date'),
                "event_name": f"{log.get('place','Session')}"[:100]
            }
    return {"event_date": None, "event_name": "Session Not Found"}

def style_feedback_text(text):
    """Styles specific tags in feedback text with colors and bold."""
    for tag, color in FEEDBACK_TAG_COLORS.items():
        replacement = f'<strong style="color:{color};">{tag}</strong>'
        text = text.replace(tag, replacement)
    return text

# --- Tab Display Functions ---
def display_level_performance_tab(all_records, user_profiles, discipline_keys, lang):
    """
    Displays the aggregated performances by certification level, with a unique color for each level.
    """
    if not all_records:
        st.info(_("no_ranking_data", lang))
        return

    records_df = pd.DataFrame(all_records)

    # Prepare profiles data
    profiles_list = []
    for user, profile_data in user_profiles.items():
        profiles_list.append({
            'user': user,
            'certification': profile_data.get('certification', _("no_certification_option", lang))
        })
    profiles_df = pd.DataFrame(profiles_list)

    if profiles_df.empty:
        st.info(_("no_stats_data", lang))
        return

    # Merge records with profiles
    merged_df = pd.merge(records_df, profiles_df, on='user', how='left')
    merged_df['certification'].fillna(_("no_certification_option", lang), inplace=True)

    # Filter out records without a parsed value
    merged_df = merged_df.dropna(subset=['parsed_value'])

    if merged_df.empty:
        st.info(_("no_stats_data", lang))
        return

    # Get best performance for each user in each discipline
    idx = merged_df.groupby(['user', 'discipline'])['parsed_value'].idxmax()
    if discipline_keys and is_lower_better(discipline_keys[0]):
        idx = merged_df.groupby(['user', 'discipline'])['parsed_value'].idxmin()

    best_perf_df = merged_df.loc[idx]

    # Define the order and color scheme for certifications based on the provided image
    cert_order = ["NB", "A1", "A2", "A3", "S4", "I1", "I2", "I3", _("no_certification_option", lang)]
    cert_colors = [
        "#D074B9",  # NB - Non-Breveté (Pink/Purple)
        "#67C27F",  # A1 - Apnéiste Débutant (Green)
        "#F2B760",  # A2 - Apnéiste Avancé (Light Orange)
        "#F28F3B",  # A3 - Apnéiste Expert (Dark Orange)
        "#2F788C",  # S4 - Assistant-Instructeur (Blue/Teal)
        "#265F70",  # I1 - A darker shade for instructors
        "#1D4654",  # I2 - Even darker
        "#132D38",  # I3 - Darkest
        "#CCCCCC"   # No Certification (Grey)
    ]

    sub_tabs = st.tabs([_("disciplines." + key, lang) for key in discipline_keys])

    for i, disc_key in enumerate(discipline_keys):
        with sub_tabs[i]:
            # st.subheader(f"{_('certification_stats_header', lang)} - {_('disciplines.' + disc_key, lang)}")

            discipline_df = best_perf_df[best_perf_df['discipline'] == disc_key]

            if discipline_df.empty:
                st.info(_("no_stats_data", lang))
                continue

            # Aggregate data: calculate mean for each certification level
            agg_df = discipline_df.groupby('certification')['parsed_value'].mean().reset_index()
            agg_df['certification'] = pd.Categorical(agg_df['certification'], categories=cert_order, ordered=True)
            agg_df = agg_df.sort_values('certification')

            # Prepare data for chart
            if is_time_based_discipline(disc_key):
                y_axis_title = f"{_('avg_performance_col', lang)} ({_('seconds_unit', lang)})"
                agg_df['formatted_perf'] = agg_df['parsed_value'].apply(format_seconds_to_static_time)
            else:
                y_axis_title = f"{_('avg_performance_col', lang)} ({_('meters_unit', lang)})"
                agg_df['formatted_perf'] = agg_df['parsed_value'].apply(lambda x: f"{int(x)}m")

            # Create the bar chart
            chart = alt.Chart(agg_df).mark_bar().encode(
                y=alt.Y('certification:N', title=_("certification_level_col", lang), sort=cert_order),
                x=alt.X('parsed_value:Q', title=y_axis_title, scale=alt.Scale(zero=False)),
                color=alt.Color('certification:N',
                                 scale=alt.Scale(domain=cert_order, range=cert_colors),
                                 legend=None
                                ),
                tooltip=[
                    alt.Tooltip('certification', title=_("certification_level_col", lang)),
                    alt.Tooltip('formatted_perf', title=_("avg_performance_col", lang))
                ]
            ).properties(
                width=alt.Step(40),
                height=250
            )

            # Add text labels on bars
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,
                color='black'
            ).encode(
                text='formatted_perf:N'
            )

            st.altair_chart(chart + text, use_container_width=True)

def display_login_form(config, lang):
    """Displays the login form and handles authentication."""
    with st.sidebar:
        st.title("Connexion")
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            user_data = config['credentials']['usernames'].get(username.lower())
            if user_data and verify_password(password, user_data['password']):
                st.session_state['authentication_status'] = True
                st.session_state['name'] = user_data['name']
                st.rerun()
            else:
                st.error(_("login_error", lang))

def main_app():
    # --- Main Application (after successful login) ---
    lang = st.session_state.language
    # Load all data at the beginning of the script run.
    # The @st.cache_data decorator will ensure these are read from file only when necessary.
    training_log_loaded = load_training_log()
    all_records_loaded = load_records(training_log_loaded)
    user_profiles = load_user_profiles()
    instructor_feedback_loaded = load_instructor_feedback()

    current_user = st.session_state.get("name")
    is_admin_view_authorized = current_user in PRIVILEGED_USERS
    is_super_admin_view_authorized = current_user in SUPER_PRIVILEGED_USERS
    
    with st.sidebar:
        st.write(f"Bienvenue *{current_user}*")
        if st.button(_("logout_button", lang)):
            st.session_state['authentication_status'] = False
            st.session_state['name'] = None
            st.rerun()
        
        # Profile Section
        user_profile_data_sidebar = user_profiles.get(current_user, {})
        with st.expander(_("profile_header_sidebar", lang)):
            with st.form(key="profile_form_sidebar_main", border=False):
                current_certification_sidebar = user_profile_data_sidebar.get("certification", _("no_certification_option", lang))
                cert_level_keys_from_dict_sidebar = list(TRANSLATIONS[lang]["certification_levels"].keys())
                actual_selectbox_options_sidebar = [_("no_certification_option", lang)] + cert_level_keys_from_dict_sidebar
                try:
                    current_cert_index_sidebar = actual_selectbox_options_sidebar.index(current_certification_sidebar)
                except ValueError:
                    current_cert_index_sidebar = 0

                st.selectbox(
                    _("certification_label", lang), options=actual_selectbox_options_sidebar,
                    index=current_cert_index_sidebar, key="certification_select_profile_form_sb"
                )

                current_cert_date_str_sidebar = user_profile_data_sidebar.get("certification_date")
                current_cert_date_obj_sidebar = None
                if current_cert_date_str_sidebar:
                    try:
                        current_cert_date_obj_sidebar = date.fromisoformat(current_cert_date_str_sidebar)
                    except ValueError:
                        current_cert_date_obj_sidebar = None

                st.date_input(
                    _("certification_date_label", lang), value=current_cert_date_obj_sidebar, key="cert_date_profile_form_sb"
                )
                st.text_input(
                    _("lifras_id_label", lang), value=user_profile_data_sidebar.get("lifras_id", ""), key="lifras_id_profile_form_sb"
                )
                st.checkbox(
                    _("anonymize_results_label", lang), value=user_profile_data_sidebar.get("anonymize_results", False), key="anonymize_profile_form_sb"
                )
                st.checkbox(
                    _("consent_ai_feedback_label", lang), value=user_profile_data_sidebar.get("consent_ai_feedback", False), key="consent_ai_feedback_profile_form_sb"
                )
                st.text_area(
                    "Motivations à faire de l'apnée :",
                    value=user_profile_data_sidebar.get("motivations", ""),
                    key="motivations_profile_form_sb"
                )
                st.text_area(
                    "Où vous imaginez vous dans votre pratique de l'apnée dans 3 ans ?",
                    value=user_profile_data_sidebar.get("projection_3_ans", ""),
                    key="projection_3_ans_profile_form_sb"
                )
                st.text_area(
                    "Texte pour le portrait photo",
                    value=user_profile_data_sidebar.get("portrait_photo_text", ""),
                    key="portrait_photo_text_profile_form_sb"
                )

                if st.form_submit_button(_("save_profile_button", lang)):
                    profiles_to_save = user_profiles.copy()
                    user_profile = profiles_to_save.get(current_user, {}).copy()

                    user_profile["certification"] = st.session_state.certification_select_profile_form_sb
                    cert_date_val = st.session_state.cert_date_profile_form_sb
                    user_profile["certification_date"] = cert_date_val.isoformat() if cert_date_val else None
                    user_profile["lifras_id"] = st.session_state.lifras_id_profile_form_sb.strip()
                    user_profile["anonymize_results"] = st.session_state.anonymize_profile_form_sb
                    user_profile["consent_ai_feedback"] = st.session_state.consent_ai_feedback_profile_form_sb
                    user_profile["motivations"] = st.session_state.motivations_profile_form_sb.strip()
                    user_profile["projection_3_ans"] = st.session_state.projection_3_ans_profile_form_sb.strip()
                    user_profile["portrait_photo_text"] = st.session_state.portrait_photo_text_profile_form_sb.strip()
                    
                    profiles_to_save[current_user] = user_profile
                    
                    save_user_profiles(profiles_to_save)
                    st.success(_("profile_saved_success", lang, user=current_user))
                    st.rerun()

        # --- Sidebar Logging Forms ---
        is_sidebar_instructor_section_visible = False
        if is_admin_view_authorized and current_user in user_profiles:
            user_cert_sidebar = user_profiles[current_user].get("certification")
            if user_cert_sidebar in INSTRUCTOR_CERT_LEVELS_FOR_LOGGING_FEEDBACK_SIDEBAR:
                is_sidebar_instructor_section_visible = True

        if is_sidebar_instructor_section_visible:
            st.header(_("log_training_header_sidebar", lang))
            with st.form(key="log_training_form_sidebar"):
                st.date_input(_("training_date_label", lang), date.today(), key="training_date_form_key")
                st.text_input(_("training_place_label", lang), value=st.session_state.training_place_buffer, key="training_place_form_key")
                st.text_area(_("training_description_label", lang), value=st.session_state.training_desc_buffer, key="training_desc_form_key")
                if st.form_submit_button(_("save_training_button", lang)):
                    desc_to_save = st.session_state.training_desc_form_key.strip()
                    place_to_save = st.session_state.training_place_form_key.strip()
                    date_to_save = st.session_state.training_date_form_key
                    if not desc_to_save:
                        st.error(_("training_description_empty_error", lang))
                    else:
                        new_training_entry = {"id": uuid.uuid4().hex, "date": date_to_save.isoformat(), "place": place_to_save, "description": desc_to_save}
                        training_log_loaded.append(new_training_entry)
                        save_training_log(training_log_loaded)
                        st.success(_("training_session_saved_success", lang))
                        st.session_state.training_place_buffer = ""
                        st.session_state.training_desc_buffer = ""
                        st.rerun()

        st.header(_("log_performance_header", lang))
        with st.form(key="log_performance_form_sidebar_main"):
            st.write(_("logging_for", lang, user=current_user))
            if not training_log_loaded:
                st.warning("Veuillez d'abord créer une activité.")
                st.form_submit_button(_("save_performance_button", lang), disabled=True)
            else:
                discipline_keys = ["Dynamic Bi-fins (DYN-BF)", "Static Apnea (STA)", "Dynamic No-fins (DNF)", "Depth (CWT/FIM)", "Depth (VWT/NLT)", "16x25m Speed Endurance"]
                translated_disciplines_for_display = [_("disciplines." + key, lang) for key in discipline_keys]
                training_session_options = {ts.get('id'): f"{ts.get('date')} - {ts.get('place', 'N/A')}" for ts in sorted(training_log_loaded, key=lambda x: x.get('date', '1900-01-01'), reverse=True)}
                selected_training_session_id = st.selectbox(
                    _("link_training_session_label", lang), options=list(training_session_options.keys()),
                    format_func=lambda x: training_session_options[x], key="log_perf_session_select_widget_key"
                )
                selected_translated_discipline = st.selectbox(
                    _("discipline", lang), translated_disciplines_for_display, key="log_discipline_perf_form_widget_key"
                )
                log_discipline_original_key_perf_form = [k for k, v in TRANSLATIONS[lang]['disciplines'].items() if v == selected_translated_discipline][0]
                performance_help_text_perf_form = _("sta_help", lang) if is_time_based_discipline(log_discipline_original_key_perf_form) else _("dyn_depth_help", lang)
                st.text_input(
                    _("performance_value", lang), value=st.session_state.log_perf_input_buffer,
                    help=performance_help_text_perf_form, key="log_perf_input_form_widget_key"
                )
                if st.form_submit_button(_("save_performance_button", lang)):
                    current_log_perf_str = st.session_state.log_perf_input_form_widget_key.strip()
                    if not current_log_perf_str:
                        st.error(_("performance_value_empty_error", lang))
                    else:
                        parsed_value_for_storage = parse_static_time_to_seconds(current_log_perf_str, lang) if is_time_based_discipline(log_discipline_original_key_perf_form) else parse_distance_to_meters(current_log_perf_str, lang)
                        if parsed_value_for_storage is not None:
                            new_record = {
                                "id": uuid.uuid4().hex, "user": current_user, "entry_date": date.today().isoformat(),
                                "discipline": log_discipline_original_key_perf_form, "original_performance_str": current_log_perf_str,
                                "parsed_value": parsed_value_for_storage, "linked_training_session_id": selected_training_session_id
                            }
                            all_records_loaded.append(new_record)
                            save_records(all_records_loaded)
                            st.success(_("performance_saved_success", lang, user=current_user))
                            st.session_state.log_perf_input_buffer = ""
                            st.rerun()

        if is_sidebar_instructor_section_visible:
            st.header(_("log_feedback_header_sidebar", lang))
            with st.form(key="log_feedback_form_sidebar"):
                all_known_users_list = sorted(list(set(r['user'] for r in all_records_loaded).union(set(user_profiles.keys()))))
                if not all_known_users_list:
                    st.warning("Please add freedivers before logging feedback.")
                else:
                    freediver_options_for_feedback = [_("select_freediver_prompt", lang)] + all_known_users_list
                    default_fb_user_idx = 0
                    try:
                        if st.session_state.feedback_for_user_buffer not in freediver_options_for_feedback:
                            st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", lang)
                        default_fb_user_idx = freediver_options_for_feedback.index(st.session_state.feedback_for_user_buffer)
                    except (ValueError, KeyError):
                        st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", lang)

                    st.selectbox(
                        _("feedback_for_freediver_label", lang), options=freediver_options_for_feedback,
                        index=default_fb_user_idx, key="feedback_for_user_selectbox_key_in_form"
                    )
                    
                    training_session_options_fb_form = {log['id']: f"{log.get('date', '')} - {log.get('place', '')}" for log in sorted(training_log_loaded, key=lambda x: x.get('date', '1900-01-01'), reverse=True)}
                    training_session_options_display_fb_form = [_("select_training_prompt", lang)] + list(training_session_options_fb_form.values())
                    default_fb_ts_idx = 0
                    try:
                        if st.session_state.feedback_training_session_buffer not in training_session_options_display_fb_form:
                            st.session_state.feedback_training_session_buffer = _("select_training_prompt", lang)
                        default_fb_ts_idx = training_session_options_display_fb_form.index(st.session_state.feedback_training_session_buffer)
                    except (ValueError, KeyError):
                        st.session_state.feedback_training_session_buffer = _("select_training_prompt", lang)

                    st.selectbox(
                        _("training_session_label", lang), options=training_session_options_display_fb_form,
                        index=default_fb_ts_idx, key="feedback_training_session_selectbox_key_in_form"
                    )
                    st.write(f"{_('instructor_name_label', lang)} {current_user}")
                    st.text_area(
                        _("feedback_text_label", lang), value=st.session_state.feedback_text_buffer,
                        key="feedback_text_area_key_in_form"
                    )
                    if st.form_submit_button(_("save_feedback_button", lang)):
                        sel_fb_for_user = st.session_state["feedback_for_user_selectbox_key_in_form"]
                        sel_fb_training_disp = st.session_state["feedback_training_session_selectbox_key_in_form"]
                        sel_fb_text = st.session_state["feedback_text_area_key_in_form"].strip()
                        sel_fb_training_id = next((log_id for log_id, display_str in training_session_options_fb_form.items() if display_str == sel_fb_training_disp), None) if sel_fb_training_disp != _("select_training_prompt", lang) else None
                        if sel_fb_for_user == _("select_freediver_prompt", lang):
                            st.error("Please select a freediver for the feedback.")
                        elif not current_user:
                            st.error("Instructor not identified.")
                        elif not sel_fb_text:
                            st.error(_("feedback_text_empty_error", lang))
                        else:
                            new_feedback = {
                                "id": uuid.uuid4().hex, "feedback_date": date.today().isoformat(), "diver_name": sel_fb_for_user,
                                "training_session_id": sel_fb_training_id, "instructor_name": current_user, "feedback_text": sel_fb_text
                            }
                            instructor_feedback_loaded.append(new_feedback)
                            save_instructor_feedback(instructor_feedback_loaded)
                            st.success(_("feedback_saved_success", lang))
                            st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", lang)
                            st.session_state.feedback_training_session_buffer = _("select_training_prompt", lang)
                            st.session_state.feedback_text_buffer = ""
                            st.rerun()

    st.title(_("app_title", lang))
    
    # Define all possible tab labels
    tab_label_freedivers = _("freedivers_tab_title", lang)
    tab_label_main_training_log = _("training_log_tab_title", lang)
    tab_label_performances = _("performances_main_tab_title", lang)
    tab_label_main_feedback_log = _("feedback_log_tab_title", lang)

    # Define the base tabs order
    tabs_to_display_names = [
        tab_label_main_training_log,
        tab_label_performances,
        tab_label_main_feedback_log,
    ]
    # Add admin-specific tab at the end
    if is_admin_view_authorized:
        tabs_to_display_names.append(f"{tab_label_freedivers}")
    
    tab_objects_main = st.tabs(tabs_to_display_names)
    tab_map = dict(zip(tabs_to_display_names, tab_objects_main))

    # --- Populate Tabs ---
    # Activités Tab
    with tab_map[tab_label_main_training_log]:
        sub_tab_definitions = [_("training_sessions_sub_tab_label", lang)]
        if is_admin_view_authorized:
            sub_tab_definitions.append(f"{_('edit_training_sessions_sub_tab_label', lang)}")
        training_sub_tabs = st.tabs(sub_tab_definitions)
        with training_sub_tabs[0]:
            if not training_log_loaded:
                st.info(_("no_training_sessions_logged", lang))
            else:
                years = sorted(list(set(datetime.fromisoformat(entry['date']).year for entry in training_log_loaded if entry.get('date'))), reverse=True)
                places = sorted(list(set(entry['place'] for entry in training_log_loaded if entry.get('place'))))
                months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                months_translated = [_("months." + m, lang) for m in months_en]
                all_tags = sorted(list(FEEDBACK_TAG_COLORS.keys()))
                
                col1, col2, col3, col4 = st.columns(4)
                with col1: selected_year = st.selectbox(_("filter_by_year_label", lang), [_("all_years_option", lang)] + years, key="training_year_filter")
                with col2: selected_month_name = st.selectbox(_("filter_by_month_label", lang), [_("all_months_option", lang)] + months_translated, key="training_month_filter")
                with col3: selected_place = st.selectbox(_("filter_by_place_label", lang), [_("all_places_option", lang)] + places, key="training_place_filter")
                with col4: selected_tag = st.selectbox(_("filter_by_tag_label", lang), [_("all_tags_option", lang)] + all_tags, key="training_tag_filter")

                
                filtered_logs = training_log_loaded
                if selected_year != _("all_years_option", lang): filtered_logs = [log for log in filtered_logs if log.get('date') and datetime.fromisoformat(log['date']).year == selected_year]
                if selected_month_name != _("all_months_option", lang):
                    month_number = months_translated.index(selected_month_name) + 1
                    filtered_logs = [log for log in filtered_logs if log.get('date') and datetime.fromisoformat(log['date']).month == month_number]
                if selected_place != _("all_places_option", lang): filtered_logs = [log for log in filtered_logs if log.get('place') == selected_place]
                
                if selected_tag != _("all_tags_option", lang):
                    logs_with_tag_ids = set()
                    for log in filtered_logs:
                        if selected_tag in log.get('description', ''):
                            logs_with_tag_ids.add(log['id'])
                            continue
                    
                    filtered_logs = [log for log in filtered_logs if log.get('id') in logs_with_tag_ids]

                if not filtered_logs:
                    st.info("No training sessions match the selected filters.")
                else:
                    for entry in sorted(filtered_logs, key=lambda x: x.get('date', '1900-01-01'), reverse=True):
                        with st.expander(f"**{entry.get('date', 'N/A')} - {entry.get('place', 'N/A')}**", expanded=True):
                            styled_text = style_feedback_text(entry.get('description', _("no_description_available", lang)))
                            st.markdown(styled_text, unsafe_allow_html=True)
                            
        
        if is_admin_view_authorized and len(training_sub_tabs) > 1:
            with training_sub_tabs[1]:
                if not training_log_loaded:
                    st.info(_("no_training_sessions_logged", lang))
                else:
                    training_log_display = [
                        {
                            "id": entry.get("id"),
                            _("training_date_label", lang): date.fromisoformat(entry["date"]) if entry.get("date") else None,
                            _("training_place_label", lang): entry.get("place"),
                            _("training_description_label", lang): entry.get("description"),
                            _("history_delete_col_editor", lang): False
                        }
                        for entry in sorted(training_log_loaded, key=lambda x: x.get('date', '1900-01-01'), reverse=True)
                    ]
                    with st.form(key="training_log_edit_form", border=False):
                        edited_training_df = st.data_editor(
                            pd.DataFrame(training_log_display),
                            column_config={
                                "id": None,
                                _("training_date_label", lang): st.column_config.DateColumn(required=True, format="YYYY-MM-DD"),
                                _("training_place_label", lang): st.column_config.TextColumn(required=True),
                                _("training_description_label", lang): st.column_config.TextColumn(required=True),
                                _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(default=False)
                            },
                            hide_index=True, key="training_log_editor", num_rows="dynamic"
                        )
                        if st.form_submit_button(_("save_training_log_changes_button", lang)):
                            new_log_list = []
                            for row in edited_training_df.to_dict('records'):
                                if row[_("history_delete_col_editor", lang)]:
                                    continue
                                
                                # Ensure 'id' exists for existing records, generate for new ones
                                record_id = row.get("id") or uuid.uuid4().hex
                                new_log_list.append({
                                    "id": record_id,
                                    "date": row[_("training_date_label", lang)].isoformat() if isinstance(row[_("training_date_label", lang)], date) else str(row[_("training_date_label", lang)]),
                                    "place": row[_("training_place_label", lang)],
                                    "description": row[_("training_description_label", lang)]
                                })

                            deleted_ids = set(log['id'] for log in training_log_loaded) - set(log['id'] for log in new_log_list if log.get('id'))
                            if deleted_ids:
                                for rec in all_records_loaded:
                                    if rec.get('linked_training_session_id') in deleted_ids: rec['linked_training_session_id'] = None
                                save_records(all_records_loaded)
                            save_training_log(new_log_list)
                            st.success(_("training_log_updated_success", lang))
                            st.rerun()

    # Performances Tab
    with tab_map[tab_label_performances]:
        perf_sub_tabs_labels = [
            _("personal_records_tab_label", lang),
            _("club_level_performance_tab_title", lang),
        ]

        # Conditionally add the "Classement" tab for super admins
        if is_super_admin_view_authorized:
            perf_sub_tabs_labels.append(f"{_('club_performances_overview_tab_label', lang)}")

        # Conditionally add other admin tabs for regular admins
        if is_admin_view_authorized:
            perf_sub_tabs_labels.extend([
                f"{_('performances_overview_tab_label', lang)}",
                f"{_('edit_performances_sub_tab_label', lang)}"
            ])

        perf_sub_tabs = st.tabs(perf_sub_tabs_labels)
        perf_sub_tab_map = dict(zip(perf_sub_tabs_labels, perf_sub_tabs))


        with perf_sub_tab_map[_("personal_records_tab_label", lang)]:
            user_records_for_tab = [r for r in all_records_loaded if r['user'] == current_user]
            if not user_records_for_tab:
                st.info(_("no_performances_yet", lang))
            else:
                with st.container(border=True):
                    discipline_keys = ["Dynamic Bi-fins (DYN-BF)", "Static Apnea (STA)", "Dynamic No-fins (DNF)", "Depth (CWT/FIM)", "Depth (VWT/NLT)", "16x25m Speed Endurance"]
                    pbs_tab = {}
                    for disc_key_pb_tab in discipline_keys:
                        disc_records_pb_tab = [r for r in user_records_for_tab if r['discipline'] == disc_key_pb_tab and r.get('parsed_value') is not None]
                        if not disc_records_pb_tab:
                            pbs_tab[disc_key_pb_tab] = ("N/A", "N/A", "N/A")
                            continue
                        best_record_pb_tab = min(disc_records_pb_tab, key=lambda x: x['parsed_value']) if is_lower_better(disc_key_pb_tab) else max(disc_records_pb_tab, key=lambda x: x['parsed_value'])
                        pb_value_formatted_tab = format_seconds_to_static_time(best_record_pb_tab['parsed_value']) if is_time_based_discipline(disc_key_pb_tab) else f"{int(best_record_pb_tab['parsed_value'])}m"
                        session_details = get_training_session_details(best_record_pb_tab.get('linked_training_session_id'), training_log_loaded)
                        pbs_tab[disc_key_pb_tab] = (pb_value_formatted_tab, session_details['event_name'], session_details['event_date'])

                    cols_pb_tab = st.columns(len(discipline_keys))
                    for i_pb_col_tab, disc_key_pb_col_tab in enumerate(discipline_keys):
                        val_tab, event_name_tab, event_date_tab = pbs_tab.get(disc_key_pb_col_tab)
                        with cols_pb_tab[i_pb_col_tab]:
                            metric_label = _("pb_labels." + disc_key_pb_col_tab, lang)
                            st.metric(label=metric_label, value=val_tab)
                            if event_date_tab:
                                st.caption(_("achieved_on_event_caption", lang, event_name=event_name_tab, event_date=event_date_tab))
                            elif val_tab == "N/A":
                                st.caption(_("no_record_yet_caption", lang))
                st.markdown("")
                sub_tab_titles_user = [_("disciplines." + key, lang) for key in discipline_keys]
                sub_tabs_user = st.tabs(sub_tab_titles_user)
                for i_sub_tab_user, disc_key_sub_tab_user in enumerate(discipline_keys):
                    with sub_tabs_user[i_sub_tab_user]:
                        chart_data_list = [
                            {
                                "Event Date": pd.to_datetime(get_training_session_details(r_chart.get('linked_training_session_id'), training_log_loaded).get('event_date')),
                                "PerformanceValue": r_chart['parsed_value'],
                                "Event Name": get_training_session_details(r_chart.get('linked_training_session_id'), training_log_loaded).get('event_name')
                            }
                            for r_chart in sorted(user_records_for_tab, key=lambda x: get_training_session_details(x.get('linked_training_session_id'), training_log_loaded).get('event_date') or '1900-01-01')
                            if r_chart['discipline'] == disc_key_sub_tab_user and r_chart.get('parsed_value') is not None and get_training_session_details(r_chart.get('linked_training_session_id'), training_log_loaded).get('event_date')
                        ]
                        st.markdown(f"#### {_('performance_evolution_subheader', lang)}")
                        if chart_data_list:
                            chart_df = pd.DataFrame(chart_data_list)
                            y_axis_title = _("performance_value", lang)
                            tooltip_list = ['Event Date:T', 'Event Name:N']
                            if is_time_based_discipline(disc_key_sub_tab_user):
                                chart_df['PerformanceValueMinutes'] = chart_df['PerformanceValue'] / 60
                                y_axis_title += f" ({_('minutes_unit', lang)})"
                                y_encoding_field = 'PerformanceValueMinutes:Q'
                                tooltip_list.insert(1, alt.Tooltip('PerformanceValueMinutes:Q', title=_('performance_value', lang) + f" ({_('minutes_unit', lang)})", format=".2f"))
                            else:
                                y_axis_title += f" ({_('meters_unit', lang)})"
                                y_encoding_field = 'PerformanceValue:Q'
                                tooltip_list.insert(1, alt.Tooltip('PerformanceValue:Q', title=_('performance_value', lang) + f" ({_('meters_unit', lang)})"))
                            chart = alt.Chart(chart_df).mark_line(point=True).encode(
                                x=alt.X('Event Date:T', title=_("history_event_date_col", lang)),
                                y=alt.Y(y_encoding_field, title=y_axis_title, scale=alt.Scale(zero=False)),
                                tooltip=tooltip_list
                            ).interactive()
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.caption(_("no_data_for_graph", lang))
                        st.markdown(f"#### {_('history_table_subheader', lang)}")
                        history_for_editor_raw = [r for r in user_records_for_tab if r['discipline'] == disc_key_sub_tab_user]
                        if not history_for_editor_raw:
                            st.caption(_("no_history_display", lang))
                        else:
                            training_session_options = {ts.get('id'): f"{ts.get('date')} - {ts.get('place', 'N/A')}" for ts in sorted(training_log_loaded, key=lambda x: x.get('date', '1900-01-01'), reverse=True)}
                            # Add "None" option for unlinked sessions
                            training_session_options[None] = _("no_specific_session_option", lang)
                            
                            session_display_to_id = {v: k for k, v in training_session_options.items()}
                            history_for_editor_display = [
                                {
                                    "id": rec.get("id"),
                                    _("link_training_session_label", lang): training_session_options.get(rec.get("linked_training_session_id"), _("no_specific_session_option", lang)),
                                    _("history_performance_col", lang): rec.get("original_performance_str", ""), # Use original_performance_str here
                                    _("history_delete_col_editor", lang): False
                                }
                                for rec in sorted(history_for_editor_raw, key=lambda x: get_training_session_details(x.get('linked_training_session_id'), training_log_loaded).get('event_date') or '1900-01-01', reverse=True)
                            ]
                            with st.form(key=f"personal_history_form_{disc_key_sub_tab_user}", border=False):
                                # Define column config dynamically based on discipline type
                                performance_column_config = {}
                                if is_time_based_discipline(disc_key_sub_tab_user):
                                    # For time-based, still display as text (MM:SS) but allow parsing
                                    # Streamlit's TextColumn is fine here as we parse manually on submit
                                    performance_column_config = st.column_config.TextColumn(label=_("history_performance_col", lang), required=True)
                                else:
                                    # For distance/other numeric, use NumberColumn
                                    performance_column_config = st.column_config.NumberColumn(
                                        label=_("history_performance_col", lang),
                                        required=True,
                                        format="%d m" # Example format for meters. Adjust if needed.
                                    )

                                edited_df = st.data_editor(
                                    pd.DataFrame(history_for_editor_display),
                                    column_config={
                                        "id": None,
                                        _("link_training_session_label", lang): st.column_config.SelectboxColumn(options=list(training_session_options.values()), required=True),
                                        _("history_performance_col", lang): performance_column_config, # <--- Apply dynamic config here
                                        _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(label=_("history_delete_col_editor", lang))
                                    },
                                    hide_index=True, key=f"data_editor_{current_user}_{disc_key_sub_tab_user}"
                                )
                                if st.form_submit_button(_("save_history_changes_button", lang)):
                                    records_to_process = [r for r in all_records_loaded if not(r['user'] == current_user and r['discipline'] == disc_key_sub_tab_user)]
                                    for row in edited_df.to_dict('records'):
                                        if row[_("history_delete_col_editor", lang)]:
                                            continue
                                        original_rec = next((r for r in history_for_editor_raw if r['id'] == row['id']), None)
                                        if original_rec:
                                            new_perf_str = str(row[_("history_performance_col", lang)]).strip()
                                            new_session_id = session_display_to_id.get(row[_("link_training_session_label", lang)])
                                            parsed_val = parse_static_time_to_seconds(new_perf_str, lang) if is_time_based_discipline(disc_key_sub_tab_user) else parse_distance_to_meters(new_perf_str, lang)
                                            if parsed_val is not None:
                                                original_rec['original_performance_str'] = new_perf_str
                                                original_rec['parsed_value'] = parsed_val
                                                original_rec['linked_training_session_id'] = new_session_id
                                            else:
                                                st.error(f"Invalid performance format for '{new_perf_str}'")
                                            records_to_process.append(original_rec)
                                    save_records(records_to_process)
                                    st.success(_("history_updated_success", lang))
                                    st.rerun()
        
        with perf_sub_tab_map[_("club_level_performance_tab_title", lang)]:
            display_level_performance_tab(all_records_loaded, user_profiles, discipline_keys, lang)

        # Conditionally render the content for the "Classement" tab (super admin)
        if is_super_admin_view_authorized:
            with perf_sub_tab_map[f"{_('club_performances_overview_tab_label', lang)}"]:
                if not all_records_loaded:
                    st.info(_("no_ranking_data", lang))
                else:
                    with st.container(border=True):
                        all_known_users_list = sorted(list(set(r['user'] for r in all_records_loaded).union(set(user_profiles.keys()))))
                        club_pbs = {}
                        for disc_key_club_pb in discipline_keys:
                            club_disc_records = [r for r in all_records_loaded if r['discipline'] == disc_key_club_pb and r.get('parsed_value') is not None]
                            if not club_disc_records:
                                club_pbs[disc_key_club_pb] = ("N/A", None, None, None)
                                continue
                            best_club_record = min(club_disc_records, key=lambda x: x['parsed_value']) if is_lower_better(disc_key_club_pb) else max(club_disc_records, key=lambda x: x['parsed_value'])
                            club_pb_value_formatted = format_seconds_to_static_time(best_club_record['parsed_value']) if is_time_based_discipline(disc_key_club_pb) else f"{int(best_club_record['parsed_value'])}m"
                            session_details = get_training_session_details(best_club_record.get('linked_training_session_id'), training_log_loaded)
                            club_pbs[disc_key_club_pb] = (club_pb_value_formatted, best_club_record['user'], session_details['event_name'], session_details['event_date'])
                        cols_club_pb = st.columns(len(discipline_keys))
                        for i, disc_key_club_pb_col in enumerate(discipline_keys):
                            val_club, user_club, event_name_club, event_date_club = club_pbs.get(disc_key_club_pb_col)
                            with cols_club_pb[i]:
                                metric_label_club = _("club_best_labels." + disc_key_club_pb_col, lang)
                                display_user_club = get_display_name(user_club, user_profiles, lang) if user_club else _("anonymous_freediver_name", lang)
                                st.metric(label=metric_label_club, value=val_club)
                                if user_club and event_date_club:
                                    st.caption(_("achieved_at_event_on_date_caption", lang, user=display_user_club, event_name=event_name_club, event_date=event_date_club))
                                elif val_club == "N/A":
                                    st.caption(_("no_record_yet_caption", lang))
                    st.markdown("")
                    ranking_sub_tab_titles = [_("disciplines." + key, lang) for key in discipline_keys]
                    ranking_sub_tabs = st.tabs(ranking_sub_tab_titles)
                    for i_rank_sub_tab, selected_discipline_ranking_key in enumerate(discipline_keys):
                        with ranking_sub_tabs[i_rank_sub_tab]:
                            user_pbs_for_discipline_ranking = []
                            for u_rank_tab in all_known_users_list:
                                user_specific_discipline_records_ranking = [r for r in all_records_loaded if r['user'] == u_rank_tab and r['discipline'] == selected_discipline_ranking_key and r.get('parsed_value') is not None]
                                if user_specific_discipline_records_ranking:
                                    best_record_for_user_ranking = min(user_specific_discipline_records_ranking, key=lambda x: x['parsed_value']) if is_lower_better(selected_discipline_ranking_key) else max(user_specific_discipline_records_ranking, key=lambda x: x['parsed_value'])
                                    session_details = get_training_session_details(best_record_for_user_ranking.get('linked_training_session_id'), training_log_loaded)
                                    user_pbs_for_discipline_ranking.append({
                                        "user": u_rank_tab, "parsed_value": best_record_for_user_ranking['parsed_value'],
                                        "event_date": session_details['event_date'], "event_name": session_details['event_name']
                                    })
                            sorted_rankings_tab = sorted(user_pbs_for_discipline_ranking, key=lambda x: x['parsed_value'], reverse=not is_lower_better(selected_discipline_ranking_key))
                            if not sorted_rankings_tab:
                                st.info(_("no_ranking_data", lang))
                            else:
                                # st.subheader(_("full_ranking_header", lang))
                                ranking_table_data = [
                                    {
                                        _("rank_col", lang): rank_idx + 1,
                                        _("user_col", lang): get_display_name(rank_item['user'], user_profiles, lang),
                                        _("best_performance_col", lang): format_seconds_to_static_time(rank_item['parsed_value']) if is_time_based_discipline(selected_discipline_ranking_key) else f"{int(rank_item['parsed_value'])}m",
                                        _("event_col", lang): rank_item.get('event_name', "N/A"),
                                        _("date_achieved_col", lang): rank_item.get('event_date', "N/A")
                                    }
                                    for rank_idx, rank_item in enumerate(sorted_rankings_tab)
                                ]
                                st.dataframe(pd.DataFrame(ranking_table_data), use_container_width=True, hide_index=True)
            
        # Admin-only Performance Overview and Edit Tabs
        if is_admin_view_authorized: # <--- ADDED THIS CONDITIONAL WRAPPER
            with perf_sub_tab_map[f"{_('performances_overview_tab_label', lang)}"]:
                # st.subheader(_("performances_overview_tab_label", lang))
                all_known_users_list = sorted(list(set(r['user'] for r in all_records_loaded).union(set(user_profiles.keys()))))
                col1, col2, col3 = st.columns(3)
                with col1: filter_user_perf = st.selectbox(_("filter_by_freediver_label", lang), [_("all_freedivers_option", lang)] + all_known_users_list, key="perf_log_user_filter_overview")
                with col2:
                    session_options = {s['id']: f"{s['date']} - {s['place']}" for s in training_log_loaded}
                    session_options[None] = _("no_specific_session_option", lang) # Add None option for unlinked records
                    filter_session_id_perf = st.selectbox(_("filter_by_training_session_label", lang), [_("all_sessions_option", lang)] + list(session_options.keys()), format_func=lambda x: session_options.get(x, x), key="perf_log_session_filter_overview")
                with col3:  
                    filter_discipline_perf = st.selectbox(
                        _("filter_by_discipline_label", lang),
                        options=[_("all_disciplines_option", lang)] + discipline_keys,
                        format_func=lambda k: k if k == _("all_disciplines_option", lang) else _(f"disciplines.{k}", lang),
                        key="perf_log_discipline_filter_overview"
                    )

                filtered_records = all_records_loaded
                if filter_user_perf != _("all_freedivers_option", lang): filtered_records = [r for r in filtered_records if r['user'] == filter_user_perf]
                if filter_session_id_perf != _("all_sessions_option", lang): filtered_records = [r for r in filtered_records if r.get('linked_training_session_id') == filter_session_id_perf]
                if filter_discipline_perf != _("all_disciplines_option", lang): filtered_records = [r for r in filtered_records if r['discipline'] == filter_discipline_perf]
                
                display_data = [
                    {
                        _("user_col", lang): rec["user"],
                        _("history_discipline_col", lang): _(f"disciplines.{rec['discipline']}", lang),
                        _("link_training_session_label", lang): f"{get_training_session_details(rec.get('linked_training_session_id'), training_log_loaded)['event_date']} - {get_training_session_details(rec.get('linked_training_session_id'), training_log_loaded)['event_name']}",
                        _("history_performance_col", lang): rec["original_performance_str"],
                        _("history_entry_date_col", lang): rec["entry_date"]
                    }
                    for rec in sorted(filtered_records, key=lambda x: x.get('entry_date', '1900-01-01'), reverse=True)
                ]
                st.dataframe(pd.DataFrame(display_data), hide_index=True, use_container_width=True)

            with perf_sub_tab_map[f"{_('edit_performances_sub_tab_label', lang)}"]: # <--- This block is now also conditionally rendered
                # st.subheader(_("edit_performances_sub_tab_label", lang))
                if not all_records_loaded:
                    st.info("No performances logged in the system.")
                else:
                    all_known_users_list = sorted(list(set(r['user'] for r in all_records_loaded).union(set(user_profiles.keys()))))
                    training_session_options = {log['id']: f"{log.get('date')} - {log.get('place', 'N/A')}" for log in training_log_loaded}
                    training_session_options[None] = _("no_specific_session_option", lang)
                    perf_log_data = [
                        {
                            "id": rec["id"],
                            _("user_col", lang): rec["user"],
                            _("history_discipline_col", lang): _(f"disciplines.{rec['discipline']}", lang),
                            _("link_training_session_label", lang): training_session_options.get(rec.get("linked_training_session_id")),
                            _("history_performance_col", lang): rec["original_performance_str"],
                            _("history_delete_col_editor", lang): False
                        }
                        for rec in sorted(all_records_loaded, key=lambda x: x.get('entry_date', '1900-01-01'), reverse=True)
                    ]
                    session_display_to_id = {v: k for k, v in training_session_options.items()}
                    discipline_labels = [_("disciplines."+k, lang) for k in discipline_keys]
                    discipline_label_to_key = {label: key for label, key in zip(discipline_labels, discipline_keys)}
                    
                    with st.form(key="all_performances_edit_form", border=False):
                        edited_perf_log_df = st.data_editor(
                            pd.DataFrame(perf_log_data),
                            column_config={
                                "id": None,
                                _("user_col", lang): st.column_config.SelectboxColumn(options=all_known_users_list, required=True),
                                _("history_discipline_col", lang): st.column_config.SelectboxColumn(options=discipline_labels, required=True),
                                _("link_training_session_label", lang): st.column_config.SelectboxColumn(options=list(training_session_options.values()), required=True),
                                _("history_performance_col", lang): st.column_config.TextColumn(required=True), # This one will need dynamic configuration similar to the personal history if it's not already handled.
                                _("history_delete_col_editor", lang): st.column_config.CheckboxColumn()
                            },
                            num_rows="dynamic", hide_index=True, key="all_perf_editor", use_container_width=True
                        )
                        if st.form_submit_button(_("save_all_performances_button", lang)):
                            new_records = []
                            for row in edited_perf_log_df.to_dict('records'):
                                if row[_("history_delete_col_editor", lang)]: continue
                                perf_str = str(row[_("history_performance_col", lang)]).strip()
                                discipline = discipline_label_to_key.get(row[_("history_discipline_col", lang)])
                                parsed_val = parse_static_time_to_seconds(perf_str, lang) if is_time_based_discipline(discipline) else parse_distance_to_meters(perf_str, lang)
                                if parsed_val is None:
                                    st.error(f"Invalid performance '{perf_str}' for {row[_('user_col', lang)]}. Skipping.")
                                    original_rec_if_exists = next((r for r in all_records_loaded if r['id'] == row['id']), None)
                                    if original_rec_if_exists:
                                        new_records.append(original_rec_if_exists)
                                else:
                                    original_rec = next((r for r in all_records_loaded if r['id'] == row['id']), {})
                                    new_records.append({
                                        "id": row.get("id") or uuid.uuid4().hex, "user": row[_("user_col", lang)], "discipline": discipline,
                                        "linked_training_session_id": session_display_to_id.get(row[_("link_training_session_label", lang)]),
                                        "original_performance_str": perf_str, "parsed_value": parsed_val,
                                        "entry_date": original_rec.get('entry_date', date.today().isoformat())
                                    })
                            save_records([r for r in new_records if r is not None])
                            st.success(_("all_performances_updated_success", lang))
                            st.rerun()

    # --- Unified Feedbacks Tab ---
    with tab_map[tab_label_main_feedback_log]:
        my_feedback_sub_tab_label = _("my_feedback_tab_label", lang)
        
        feedback_sub_tabs_labels = [my_feedback_sub_tab_label]
        if is_admin_view_authorized:
            feedback_sub_tabs_labels.append(f"{_('feedbacks_overview_tab_label', lang)}")
            feedback_sub_tabs_labels.append(f"{_('edit_feedbacks_sub_tab_label', lang)}")

        feedback_sub_tabs = st.tabs(feedback_sub_tabs_labels)
        feedback_sub_tab_map = dict(zip(feedback_sub_tabs_labels, feedback_sub_tabs))

        with feedback_sub_tab_map[my_feedback_sub_tab_label]:
            user_feedback = [fb for fb in instructor_feedback_loaded if fb.get('diver_name') == current_user]
            user_profile_data = user_profiles.get(current_user, {})
            has_ai_consent = user_profile_data.get("consent_ai_feedback", False)
            
            if not user_feedback:
                st.info(_("no_feedback_for_user", lang))
            
            if not has_ai_consent:
                st.warning(_("consent_ai_feedback_missing", lang))
            else:
                if user_feedback:
                    if st.button(_("generate_feedback_summary_button", lang)):
                        with st.spinner("Génération du résumé..."):
                            all_feedback_text = "\n".join([f"- {fb['feedback_text']}" for fb in user_feedback])
                            import toml
                            prompts_instructions = toml.load("./prompts.toml")
                            adeps_coaching_instructions = prompts_instructions['feedback']['adeps_coaching_instructions']
                            huron_spirit = prompts_instructions['feedback']['huron_spirit']                  
                            comparatif_brevets = prompts_instructions['feedback']['comparatif_brevets']  
                            motivations_text = user_profile_data.get("motivations", "")
                            objectifs_text = user_profile_data.get("projection_3_ans", "")
                            vision_text = user_profile_data.get("portrait_photo_text", "")
                            
                            prompt = f"""Voici une série de feedbacks pour un apnéiste. 
                            Ce feedback est donné par d'autres apnéistes et instructeurs. 
                            Tu es un coach d'apnée tel que décrit ici \n{adeps_coaching_instructions}. 
                            Tu dois analyser ces feedbacks et en tirer un résumé constructif de maximum 10 phrases pour l'apnéiste afin qu'il puisse s'améliorer. 
                            Tu dois prendre en compte le niveau actuel de l'apnéiste qui est le suivant : {user_profiles.get(current_user, {}).get('certification', 'Non spécifié')}.  
                            Tu dois également prendre en compte ses motivations à pratiquer l'apnée : {motivations_text}. 
                            Ainsi que ses objectifs de progression : {objectifs_text}. 
                            Et sa vision de l'apnée : {vision_text}. 
                            Il faut aussi que tu prennes en compte les attentes de la Lifras pour chaque niveau d'apnée pour établir où se trouve l'apnéiste dans son parcours. 
                            Voici ces attentes : {comparatif_brevets}. 
                            Voici également de la théorie d'un coach que tu peux utiliser pour étoffer ton feedback: {huron_spirit}. 
                            Ne ressors pas de ton analyse des feedbacks et autres contenus, un évènement spécifique qui pourrait être traumatisant, comme des soucis de santé par exemple, ou une mauvaise expérience. Reste en bird eye view.  
                            Les feedback sont ceux-ci:\n{all_feedback_text}. 
                            Reste concis, bienveillant, constructif et factuel. N'utilises pas de bullet lists. 
                            Tu peux mettre les recoemmndations clés en gras. 
                            Ton texte doit couvrir tous les aspects de la pratique de l'apnée, y compris la technique, la sécurité, la relaxation, et l'état d'esprit. Ainsi que les aspects de progression et de motivation. 
                            Tu dois également t'assurer que ton texte est adapté au niveau de l'apnéiste, en tenant compte de son expérience et de ses compétences actuelles. 
                            Une fois ton texte prêt, vérifie plusieurs fois pour être cetain que tu as bien appliqué les consignes ci-dessus, sinon modifie ton texte."""

                            try:
                                from google import genai
                                api_key = st.secrets["genai"]["key"]
                                client = genai.Client(api_key=api_key)
                                summary_text = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                                st.session_state['feedback_summary'] = summary_text.text
                            except Exception as e:
                                st.error(f"Erreur lors de la génération du résumé : {e}")
                    
                    if 'feedback_summary' in st.session_state and st.session_state.feedback_summary:
                        st.markdown(st.session_state['feedback_summary'])

    # Admin-only Sub-Tabs
        if is_admin_view_authorized:
            if f"{_('feedbacks_overview_tab_label', lang)}" in feedback_sub_tab_map:
                with feedback_sub_tab_map[f"{_('feedbacks_overview_tab_label', lang)}"]:
                    all_known_users_list = sorted(list(set(r['user'] for r in all_records_loaded).union(set(user_profiles.keys()))))
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        filter_user = st.selectbox(_("filter_by_freediver_label", lang), [_("all_freedivers_option", lang)] + all_known_users_list, key="fb_overview_user")
                    with col2:
                        session_options = {s['id']: f"{s.get('date', 'N/A')} - {s.get('place', 'N/A')}" for s in training_log_loaded}
                        session_options[None] = _("no_specific_session_option", lang)
                        filter_session_id = st.selectbox(_("filter_by_training_session_label", lang), [_("all_sessions_option", lang)] + list(session_options.keys()), format_func=lambda x: session_options.get(x, x), key="fb_overview_session")
                    with col3:
                        instructors = sorted(list(set(fb['instructor_name'] for fb in instructor_feedback_loaded)))
                        filter_instructor = st.selectbox(_("filter_by_instructor_label", lang), [_("all_instructors_option", lang)] + instructors, key="fb_overview_instructor")

                    filtered_feedbacks = instructor_feedback_loaded
                    if filter_user != _("all_freedivers_option", lang):
                        filtered_feedbacks = [f for f in filtered_feedbacks if f['diver_name'] == filter_user]
                    if filter_session_id != _("all_sessions_option", lang):
                        filtered_feedbacks = [f for f in filtered_feedbacks if f.get('training_session_id') == filter_session_id]
                    if filter_instructor != _("all_instructors_option", lang):
                        filtered_feedbacks = [f for f in filtered_feedbacks if f['instructor_name'] == filter_instructor]

                    if not filtered_feedbacks:
                        st.info(_("no_feedbacks_match_filters", lang))
                    else:
                        for fb in sorted(filtered_feedbacks, key=lambda x: x.get('feedback_date', '1900-01-01'), reverse=True):
                            with st.container(border=True):
                                session_details = get_training_session_details(fb.get("training_session_id"), training_log_loaded)
                                st.markdown(f"**{fb['diver_name']}** par **{fb['instructor_name']}** à **{session_details['event_name']}** le **{fb['feedback_date']}**")
                                st.markdown(fb['feedback_text'], unsafe_allow_html=True)
                                

            if f"{_('edit_feedbacks_sub_tab_label', lang)}" in feedback_sub_tab_map:
                with feedback_sub_tab_map[f"{_('edit_feedbacks_sub_tab_label', lang)}"]:
                    if not instructor_feedback_loaded:
                        st.info(_("no_feedback_in_log", lang))
                    else:
                        with st.form(key="feedback_log_edit_form", border=False):
                            all_known_users_list = sorted(list(set(r['user'] for r in all_records_loaded).union(set(user_profiles.keys()))))
                            session_options = {s['id']: f"{s.get('date', 'N/A')} - {s.get('place', 'N/A')}" for s in training_log_loaded}
                            session_options[None] = _("no_specific_session_option", lang)

                            feedback_df_data = []
                            for fb in instructor_feedback_loaded:
                                dt_obj = None
                                try:
                                    dt_obj = date.fromisoformat(fb.get("feedback_date"))
                                except (ValueError, TypeError):
                                    pass
                                feedback_df_data.append({
                                    "id": fb["id"],
                                    _("feedback_date_col", lang): dt_obj,
                                    _("feedback_for_freediver_label", lang): fb["diver_name"],
                                    _("instructor_name_label", lang): fb["instructor_name"],
                                    _("link_training_session_label", lang): session_options.get(fb.get("training_session_id")),
                                    _("feedback_text_label", lang): fb["feedback_text"],
                                    _("history_delete_col_editor", lang): False
                                })
                            
                            feedback_df = pd.DataFrame(feedback_df_data)
                            session_display_to_id = {v: k for k, v in session_options.items()}

                            edited_feedback_df = st.data_editor(
                                feedback_df,
                                column_config={
                                    "id": None,
                                    _("feedback_date_col", lang): st.column_config.DateColumn(required=True, format="YYYY-MM-DD"),
                                    _("feedback_for_freediver_label", lang): st.column_config.SelectboxColumn(options=all_known_users_list, required=True),
                                    _("instructor_name_label", lang): st.column_config.SelectboxColumn(options=all_known_users_list, required=True),
                                    _("link_training_session_label", lang): st.column_config.SelectboxColumn(options=list(session_options.values()), required=True),
                                    _("feedback_text_label", lang): st.column_config.TextColumn(required=True),
                                    _("history_delete_col_editor", lang): st.column_config.CheckboxColumn()
                                },
                                num_rows="dynamic",
                                hide_index=True,
                                key="feedback_log_editor",
                                use_container_width=True
                            )

                            if st.form_submit_button(_("save_feedback_log_changes_button", lang)):
                                new_feedback_list = []
                                for row in edited_feedback_df.to_dict('records'):
                                    if not row[_("history_delete_col_editor", lang)]:
                                        date_val = row[_("feedback_date_col", lang)]
                                        new_feedback_list.append({
                                            "id": row.get("id") or uuid.uuid4().hex,
                                            "feedback_date": date_val.isoformat() if isinstance(date_val, date) else str(date_val),
                                            "diver_name": row[_("feedback_for_freediver_label", lang)],
                                            "instructor_name": row[_("instructor_name_label", lang)],
                                            "feedback_text": row[_("feedback_text_label", lang)].strip(),
                                            "training_session_id": session_display_to_id.get(row[_("link_training_session_label", lang)])
                                        })
                                save_instructor_feedback(new_feedback_list)
                                st.success(_("feedback_log_updated_success", lang))
                                st.rerun()
            
            with tab_map.get(tab_label_freedivers, st.empty()):
                # st.subheader(_("edit_freedivers_header", lang))
                all_known_users_list = sorted(list(set(r['user'] for r in all_records_loaded).union(set(user_profiles.keys()))))
                freedivers_data_for_editor = []
                for user_name in all_known_users_list:
                    profile = user_profiles.get(user_name, {})
                    cert_date_obj = None
                    if profile.get("certification_date"):
                        try: cert_date_obj = date.fromisoformat(profile["certification_date"])
                        except (ValueError, TypeError): pass
                    freedivers_data_for_editor.append({
                        "original_name": user_name,
                        _("freediver_name_col_editor", lang): user_name,
                        _("certification_col_editor", lang): profile.get("certification", _("no_certification_option", lang)),
                        _("certification_date_col_editor", lang): cert_date_obj,
                        _("lifras_id_col_editor", lang): profile.get("lifras_id", ""),
                        _("anonymize_results_col_editor", lang): profile.get("anonymize_results", False)
                    })
                
                with st.form(key="freedivers_editor_form", border=False):
                    edited_freedivers_df = st.data_editor(
                        pd.DataFrame(freedivers_data_for_editor),
                        column_config={
                            "original_name": None,
                            _("freediver_name_col_editor", lang): st.column_config.TextColumn(required=True),
                            _("certification_col_editor", lang): st.column_config.SelectboxColumn(options=[_("no_certification_option", lang)] + list(_("certification_levels", lang).keys())),
                            _("certification_date_col_editor", lang): st.column_config.DateColumn(format="YYYY-MM-DD"),
                            _("lifras_id_col_editor", lang): st.column_config.TextColumn(),
                            _("anonymize_results_col_editor", lang): st.column_config.CheckboxColumn()
                        },
                        key="freedivers_data_editor", num_rows="dynamic", hide_index=True
                    )
                    if st.form_submit_button(_("save_freedivers_changes_button", lang)):
                        edited_rows = edited_freedivers_df.to_dict('records')
                        
                        final_profiles = user_profiles.copy()
                        new_names_from_editor = {row[_("freediver_name_col_editor", lang)].strip() for row in edited_rows}
                        
                        # Handle user deletion
                        users_to_delete = [user for user in list(final_profiles.keys()) if user not in new_names_from_editor]
                        for user_to_del in users_to_delete:
                            del final_profiles[user_to_del]

                        name_map = {}
                        all_new_names_list = [row[_("freediver_name_col_editor", lang)].strip() for row in edited_rows if row[_("freediver_name_col_editor", lang)]]
                        if len(all_new_names_list) != len(set(all_new_names_list)):
                            st.error("Duplicate names found. Please ensure all names are unique.")
                        else:
                            for row in edited_rows:
                                original_name = row.get("original_name")
                                new_name = row[_("freediver_name_col_editor", lang)].strip()
                                if not new_name: continue

                                profile_data = final_profiles.get(original_name, {}).copy() # Get existing profile or empty
                                
                                cert_date_val = row[_("certification_date_col_editor", lang)]
                                profile_data["certification"] = row[_("certification_col_editor", lang)]
                                profile_data["certification_date"] = cert_date_val.isoformat() if pd.notna(cert_date_val) and isinstance(cert_date_val, (date, datetime)) else None
                                profile_data["lifras_id"] = str(row[_("lifras_id_col_editor", lang)]).strip() if pd.notna(row[_("lifras_id_col_editor", lang)]) else ""
                                profile_data["anonymize_results"] = bool(row[_("anonymize_results_col_editor", lang)])
                                
                                if original_name and original_name != new_name:
                                    name_map[original_name] = new_name
                                    # If name changed, remove old entry if it still exists
                                    if original_name in final_profiles:
                                        del final_profiles[original_name]
                                
                                final_profiles[new_name] = profile_data

                            if name_map:
                                for rec in all_records_loaded:
                                    rec["user"] = name_map.get(rec.get("user"), rec.get("user"))
                                for fb in instructor_feedback_loaded:
                                    fb["diver_name"] = name_map.get(fb.get("diver_name"), fb.get("diver_name"))
                                    fb["instructor_name"] = name_map.get(fb.get("instructor_name"), fb.get("instructor_name"))
                                if st.session_state.get("name") in name_map:
                                    st.session_state["name"] = name_map[st.session_state.get("name")]
                            
                            save_user_profiles(final_profiles)
                            save_records(all_records_loaded)
                            save_instructor_feedback(instructor_feedback_loaded)
                            
                            st.success(_("freedivers_updated_success", lang))
                            st.rerun()

# --- Main Execution ---
def main():
    """Main function to run the Streamlit app."""
    if 'language' not in st.session_state:
        st.session_state.language = 'fr'
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    
    if 'training_place_buffer' not in st.session_state:
        st.session_state.training_place_buffer = ""
    if 'training_desc_buffer' not in st.session_state:
        st.session_state.training_desc_buffer = ""
    if 'log_perf_input_buffer' not in st.session_state:
        st.session_state.log_perf_input_buffer = ""
    if 'feedback_for_user_buffer' not in st.session_state:
        st.session_state.feedback_for_user_buffer = ""
    if 'feedback_training_session_buffer' not in st.session_state:
        st.session_state.feedback_training_session_buffer = ""
    if 'feedback_text_buffer' not in st.session_state:
        st.session_state.feedback_text_buffer = ""

    if 'feedback_summary' not in st.session_state:
        st.session_state.feedback_summary = None

    st.set_page_config(page_title=_("page_title", st.session_state.language), layout="wide", initial_sidebar_state="expanded", page_icon="🌊",)

    config = get_auth_config()

    if st.session_state['authentication_status']:
        main_app()
    else:
        display_login_form(config, st.session_state.language)


if __name__ == "__main__":
    main()