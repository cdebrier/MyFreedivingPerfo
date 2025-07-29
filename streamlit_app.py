import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import uuid
import altair as alt
import bcrypt
import gspread
from google.oauth2 import service_account
import toml

# --- Privileged User Configuration ---
PRIVILEGED_USERS = ["Philippe K.", "Vincent C.", "Charles D.B.", "Rémy L.", "Gregory D.", "Melinda M.", "Nicolas R."] 
SUPER_PRIVILEGED_USERS = ['Charles D.B.']

# Instructor certification levels for different functionalities
INSTRUCTOR_CERT_LEVELS_FOR_LOGGING_FEEDBACK_SIDEBAR = ["NB", "A1", "A2", "A3", "S4", "I1", "I2", "I3"]
INSTRUCTOR_CERT_LEVELS_FOR_ADMIN_TABS_AND_DROPDOWNS = ["A3", "S4", "I1", "I2", "I3"]

# --- Discipline Configuration ---
LOWER_IS_BETTER_DISCIPLINES = ["16x25m Speed Endurance"]

# --- Styling ---
# New structure for badge configuration, aligning with st.badge(color, icon) and markdown badges
# NOTE: For markdown badges (:color-badge[]), colors must be predefined names (red, green, blue, orange, violet, gray, etc.)
# or theme colors. Hex codes won't work directly in markdown syntax.
FEEDBACK_TAG_BADGE_CONFIG = {
    "#apnée/marche": {"color": "green", "icon": ":material/directions_walk:"},
    "#apnée/stretching": {"color": "blue", "icon": ":material/fitness_center:"},
    "#apnée/statique": {"color": "orange", "icon": ":material/timer:"}, # 'orange' is a standard named color
    "#apnée/dynamique": {"color": "red", "icon": ":material/run_circle:"},
    "#apnée/dnf": {"color": "red", "icon": ":material/barefoot:"},
    "#apnée/respiration": {"color": "blue", "icon": ":material/rib_cage:"},
    "#apnée/profondeur": {"color": "violet", "icon": ":material/water_drop:"}, # Changed from hex to 'violet' named color
}

# --- Language Translations ---
TRANSLATIONS = {
    "fr": {
        "page_title": "MacaJournal",
        "app_title": "📒 Mon Journal d'@pnée",
        "user_management_header": "👤 Gestion des Apnéistes",
        "no_users_yet": "Aucun apnéiste pour le moment. Ajoutez-en un via l'onglet Apnéistes.",
        "enter_freediver_name_sidebar": "Entrez le nom du Nouvel Apnéiste (Format: Prénom L.)",
        "confirm_freediver_button_sidebar": "Afficher les Données",
        "new_user_success": "Nouvel apnéiste : **{user}**. Profil/performance à sauvegarder pour finaliser.",
        "select_user_or_add": "Sélectionnez un apnéiste",
        "add_new_user_option": "✨ Ajouter un nouvel apnéiste...",
        "existing_user_selected": "Apnéiste **{user}** confirmé.",
        "log_performance_header": "📈 Nouvelle Performance",
        "profile_header_sidebar": "👤 Mon Profil",
        "select_user_first_warning": "Connectez-vous pour enregistrer des performances.",
        "logging_for": "Enregistrement pour : **{user}**",
        "link_training_session_label": "Activité",
        "no_specific_session_option": "Événement personnalisé / Aucune session spécifique",
        "entry_date_label": "Date d'Entrée",
        "discipline": "Discipline",
        "performance_value": "Encode ta performance ici",
        "performance_value_label":"Performance",
        "performance_comment_label": "Commentaire",
        "performance_comment_placeholder": "Notes sur la séance, sensations, matériel, etc.",
        "sta_help": "Format : MM:SS (ex: 03:45). Les millisecondes seront ignorées à l'affichage.",
        "dyn_depth_help": "Distances : un nombre entier, optionnellement suivi de 'm' (ex: **75** ou **75m**). \n\nDurées : Minutes:Secondes MM:SS (ex. **03:20**).",
        "save_performance_button": "💾 Enregistrer la performance",
        "performance_value_empty_error": "La valeur de la performance ne peut pas être vide.",
        "event_name_empty_error": "Le nom de l'événement ne peut pas être vide (si aucune session d'entraînement n'est liée).",
        "performance_saved_success": "Performance enregistrée pour {user} !",
        "process_performance_error": "Échec du traitement de la valeur de performance. Veuillez vérifier le format.",
        "my_performances_header": "📬 Mes Performances ({user})",
        "personal_records_tab_label": "📈 Mes Performances",
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
            "Dynamic Bi-fins (DYN-BF)": "Record DYNB",
            "Static Apnea (STA)": "Record STA",
            "Dynamic No-fins (DNF)": "Record DNF",
            "Depth (CWT/FIM)": "Record CWT/FIM",
            "Depth (VWT/NLT)": "Record VWT/NLT",
            "16x25m Speed Endurance": "Record 16x25m"
        },
        "achieved_at_event_on_date_caption": "Par {user} à {event_name} le {event_date}",
        "achieved_on_event_caption": "{event_name}, {event_date}",
        "no_record_yet_caption": "Aucun record pour l'instant",
        "performance_evolution_subheader": "📈 Évolution des Performances",
        "seconds_unit": "secondes",
        "meters_unit": "mètres",
        "minutes_unit": "minutes",
        "history_table_subheader": "📜 Historique des Performances (éditable)",
        "full_ranking_subheader": "📜 Historique Complet",
        "history_event_name_col": "Nom Événement",
        "history_event_date_col": "Date de l'Activité",
        "history_entry_date_col": "Date Entrée",
        "history_discipline_col": "Discipline",
        "history_performance_col": "Performance",
        "history_comment_col": "Commentaire",
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
            "Static Apnea (STA)": "Statique (STA)",
            "Dynamic Bi-fins (DYN-BF)": "Dyn. Bi-palmes (DYN-BF)",
            "Dynamic No-fins (DNF)": "Dyn. Sans Palmes (DNF)",
            "Depth (CWT/FIM)": "Prof. (CWT/FIM)",
            "Depth (VWT/NLT)": "Prof. (VWT/NLT)",
            "16x25m Speed Endurance": "Dyn. 16x25m"
        },
        "months": {
            "January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin",
            "July": "Juillet", "August": "Août", "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"
        },
        "performances_main_tab_title": "📈 Performances",
        "club_performances_overview_tab_label": "🏆 Performances du Club / Apnéiste [A]",
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
        "anonymous_freediver_name": "😎",
        "save_profile_button": "💾 Enregistrer le Profil",
        "profile_saved_success": "Profil enregistré avec succès pour {user} !",
        "select_user_to_edit_profile": "Connectez-vous pour voir ou modifier votre profil.",
        "no_certification_option": "Non Spécifié",
        "certification_levels": {
            "A1": "A1", "A2": "A2", "A3": "A3", "S4": "S4",
            "I1": "I1", "I2": "I2", "I3": "I3", "NB": "NB"
        },
        "certification_stats_header": "📈 Statistiques par Niveau de Brevet",
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
        "club_performances_tab_title": "📊 Performances du Club / Brevet",
        "club_level_performance_tab_title": "📊 Performances du Club / Brevet",
        "no_data_for_club_performance_display": "Aucune donnée de performance disponible pour le club dans cette discipline.",
        "quarterly_average_label": "Moyenne Trimestrielle",
        "freedivers_tab_title": "🤿 Apnéistes",
        "edit_freedivers_header": "🤿 Gérer les Apnéistes",
        "set_reset_password_col_editor": "Définir/Réinitialiser Mot de Passe",
        "set_reset_password_help": "Entrez un nouveau mot de passe pour le définir ou le réinitialiser. Laissez vide pour conserver le mot de passe actuel.",
        "certification_col_editor": "Niveau de Brevet",
        "certification_date_col_editor": "Date Brevet",
        "lifras_id_col_editor": "ID LIFRAS",
        "pb_sta_col_editor": "PB STA",
        "pb_dynbf_col_editor": "PB DNF",
        "pb_depth_col_editor": "PB Prof. (CWT/FIM)",
        "pb_vwt_nlt_col_editor": "PB Prof. (VWT/NLT)",
        "pb_16x25_col_editor": "PB 16x25m",
        "save_freedivers_changes_button": "💾 Sauvegarder les Modifications",
        "freedivers_updated_success": "Données des apnéistes mises à jour avec succès.",
        "freediver_name_conflict_error": "Erreur : Le nom '{new_name}' est déjà utilisé par un autre apnéiste. Veuillez choisir un nom unique.",
        "original_name_col_editor_hidden": "nom_original",
        "freediver_certification_summary_header": "🔢 Apnéistes par Niveau de Brevet",
        "count_col": "Nombre",
        "training_log_tab_title": "📅 Activités",
        "log_training_header_sidebar": "📅 Nouvelle Activité",
        "training_date_label": "Date de l'Activité",
        "training_place_label": "Lieu de l'Activité",
        "training_description_label": "Description de l'Activité",
        "training_description_placeholder":"Décris l'activité ici. Utilise des tags (#apnée/statique, #apnée/profondeur, ...) pour catégoriser l'activité et faciliter la recherche ultérieure. Tu peux aussi inclure des détails comme le lieu, les conditions, les participants, les objectifs de la séance, etc.",
        "save_training_button": "💾 Enregistrer l'Activité",
        "training_session_saved_success": "Activé enregistrée !",
        "training_description_empty_error": "La description de l'activité ne peut pas être vide.",
        "training_log_table_header": "📋 Activités (Modifiable)",
        "save_training_log_changes_button": "💾 Sauvegarder les Modifications",
        "training_log_updated_success": "Activités mise à jour avec succès.",
        "performances_overview_tab_label": "📒 Journal des Performances [A]",
        "edit_performances_sub_tab_label": "📝 Éditer des Performances [A]",
        "save_all_performances_button": "💾 Sauvegarder les Modifications",
        "all_performances_updated_success": "Journal des performances mis à jour avec succès.",
        "feedback_log_tab_label": "💬 Feedbacks",
        "my_feedback_tab_label": "💬 Mon Feedback",
        "generate_feedback_summary_button": "Générer le résumé des feedbacks",
        "feedback_summary_header": "Résumé des feedbacks",
        "no_feedback_to_summarize": "Aucun feedback à résumer pour le moment.",
        "feedbacks_overview_tab_label": "📒 Journal des Feedbacks [A]",
        "edit_feedbacks_sub_tab_label": "📝 Éditer des Feedbacks [A]",
        "log_feedback_header_sidebar": "💬 Nouveau Feedback",
        "feedback_for_freediver_label": "Apnéiste",
        "feedback_log_tab_title" : "💬 Feedbacks",
        "training_session_label": "Activité Liée :",
        "instructor_name_label": "Encadrant",
        "feedback_text_label": "Feedback",
        "feedback_text_area_ph": "Encode ton feedback sur ton activité ici. Ton feedback est aussi utilisé pour générer, si tu le souhaites, un feedback personalisé, incluant d'éventuels feedbacks constructifs de tes encadrants.",
        "save_feedback_button": "💾 Enregistrer Feedback",
        "feedback_saved_success": "Feedback enregistré avec succès !",
        "feedback_text_empty_error": "Le texte du feedback ne peut pas être vide.",
        "feedback_log_table_header": "📒 Journal des Feedbacks (Modifiable)",
        "save_feedback_log_changes_button": "💾 Sauvegarder les Modifications",
        "feedback_log_updated_success": "Journal des feedbacks mis à jour.",
        "no_feedback_for_user": "Aucun feedback reçu pour l'instant.",
        "no_feedback_in_log": "Aucun feedback enregistré dans le système.",
        "feedback_date_col": "Date Feedback",
        "select_training_prompt": "Sélectionnez une session (optionnel)",
        "select_freediver_prompt": "Sélectionnez l'Apnéiste",
        "select_instructor_prompt": "Sélectionnez l'Encadrant",
        "detailed_training_sessions_subheader": "Activités",
        "training_sessions_sub_tab_label": "📒 Journal d'Activités",
        "edit_training_sessions_sub_tab_label": "✏️ Éditer des Activités [A]",
        "no_description_available": "Aucune description disponible.",
        "no_training_sessions_logged": "Aucune activité enregistrée pour le moment.",
        "filter_by_freediver_label": "Filtrer par Apnéiste :",
        "filter_by_training_session_label": "Filtrer par Activité :",
        "filter_by_instructor_label": "Filtrer par Encadrant :",
        "filter_by_discipline_label": "Filtrer par Discipline :",
        "all_freedivers_option": "Tous les Apnéistes",
        "all_sessions_option": "Toutes les Sessions",
        "all_instructors_option": "Tous les Encadrants",
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
        "logout_button": "Déconnexion",
        "journal_freedivers_tab_label": "📒 Journal des apnéistes [A]",
        "edit_freedivers_sub_tab_label": "✏️ Éditer des apnéistes [A]",
        "freediver_name_col_editor": "Nom de l'Apnéiste",
        # --- Wish Translations ---
        "wish_header_sidebar": "💡 Nouveau Souhait",
        "wish_description_label": "Description du souhait",
        "wish_description_label_ph": "Décris tes souhaits, tes envies, tes suggestions, ce qui te passe par la tête :) ... Par exemple : j'aimerais davantage de jeux, de challenge, de sorties en mer et/ou en piscine, de cours théoriques, de séances filmées, etc.",
        "save_wish_button": "💾 Enregistrer le Souhait",
        "wish_saved_success": "Souhait enregistré avec succès !",
        "wish_description_empty_error": "La description du souhait ne peut pas être vide.",
        "wishes_main_tab_title": "💡 Souhaits",
        "wishes_log_sub_tab_label": "📒 Journal des Souhaits [A]",
        "wishes_summary_sub_tab_label": "💡 Synthèse des Souhaits [A]",
        "no_wishes_logged": "Aucun souhait enregistré pour le moment.",
        "generate_wishes_summary_button": "Générer la synthèse des souhaits",
        "wishes_summary_header": "Synthèse des Souhaits",
        "no_wishes_to_summarize": "Aucun souhait à résumer pour le moment.",
        "wish_date_col": "Date du Souhait",
        "wish_by": "Souhait de {user} le {date}",
        "edit_wishes_sub_tab_label": "✏️ Éditer des Souhaits [A]",
        "save_wishes_changes_button": "💾 Sauvegarder les Modifications des Souhaits",
        "wishes_updated_success": "Souhaits mis à jour avec succès.",
        "training_suggestion_tab_label": "💡 Suggestion d'Activité [A]",
        "generate_training_suggestion_button": "💡 Générer une nouvelle séance en piscine",
        "generating_training_suggestion_spinner": "🤖 Création d'une séance créative en cours...",
        "training_suggestion_header": "Générateur de Séances pour Encadrants",
        "training_suggestion_intro": "En cliquant sur le bouton - autant de fois que tu le souhaites - tu vas obtenir une suggestion de séance pour le groupe, basée sur les dernières activités du club et conçue pour varier les plaisirs !",
        "no_data_for_suggestion": "Pas assez de données d'activités pour générer une suggestion. Veuillez d'abord enregistrer des activités.",
        "suggestion_copy_helper": "Voici une suggestion de séance. Vous pouvez la copier et la coller dans la description d'une nouvelle activité.",
        "suggestion_generation_error": "Désolé, la génération de la suggestion a échoué. Veuillez réessayer.",
        "api_call_error": "Erreur lors de l'appel à l'API de génération : {e}",
        "avg_performance_by_certification_header" : "📊 Performance Moyenne par Niveau de Brevet",
        "freediver_certification_summary_header": "🔢 Apnéistes par Niveau de Brevet",
        "freediver_certification_chart_tab_label": "📊 Apnéistes par Brevet [A]",
        "count_col": "Nombre",
        "feedbacks_by_apneist_chart_tab_label": "🔢 Feedbacks par Apnéistes [A]",
        "my_self_feedbacks_header": "Mes auto-feedbacks",
        "no_self_feedbacks_yet": "Vous ne vous êtes encore donné aucun feedback.",
        "self_feedback_event_col": "Événement",
        "self_feedback_date_col": "Date de l'événement",
        "self_feedback_text_col": "Feedback",
        "club_label": "Club :",
        "all_clubs_option": "Tous les Clubs",
        "filter_by_club_label": "Filtrer par Club :",
        "new_club_header_sidebar": "➕ Nouveau Club",
        "new_club_name_label": "Nom du nouveau club",
        "save_new_club_button": "💾 Créer le club",
        "club_saved_success": "Club '{club_name}' créé avec succès !",
        "club_name_empty_error": "Le nom du club ne peut pas être vide.",
        "club_name_exists_error": "Le club '{club_name}' existe déjà.",
        "new_club_name_placeholder":"Nom du nouveau club",
        "new_freediver_header_sidebar": "✨ Nouvel Apnéiste",
        "freediver_full_name_label": "Prénom et Nom",
        "save_new_freediver_button": "💾 Ajouter l'apnéiste",
        "new_freediver_success": "Nouvel apnéiste '{user_name}' ajouté avec succès au club '{club_name}' !",
        "freediver_name_empty_error": "Le prénom et le nom de famille ne peuvent pas être vides.",
        "freediver_exists_error": "L'apnéiste '{user_name}' existe déjà.",
        "club_owner_missing_club": "En tant que propriétaire de club, vous devez avoir un club défini dans votre profil pour ajouter de nouveaux apnéistes.",
        "freediver_full_name_placeholder": "Prénom Nom (ex: Jean Dupont)",
        "motivations_placeholder": "Quelles sont mes motivations à pratiquer l'apnée ?",
        "projection_3_ans_placeholder": "Où me vois-je dans 3 ans en apnée ?",
        "portrait_photo_text_placeholder": "Il s'agit de la légende qui sera ajouté sous ton portrait d'apnéiste. Sens-toi libre ! Prose, humour, sérieux, ... C'est comme tu veux :)",
    }
}


# --- Helper to get translated text ---
def _(key, lang='fr', **kwargs):
    """
    Gets a translated string for the given key.
    Since only French is available, it always uses the 'fr' dictionary.
    """
    keys = key.split('.')
    translation_set = TRANSLATIONS['fr']

    value = translation_set
    try:
        for k_loop in keys:
            value = value[k_loop]
        if kwargs:
            return value.format(**kwargs)
        return value
    except KeyError:
        return key

# --- Helper for anonymization ---
def get_display_name(user_name, user_profiles_current_load, lang):
    """
    Gets a display name for a user, respecting anonymization settings.
    `user_profiles_current_load` should be the full `user_profiles_all` dictionary.
    """
    if user_name and user_name in user_profiles_current_load:
        if user_profiles_current_load[user_name].get("anonymize_results", False):
            return _("anonymous_freediver_name", lang)
    return user_name

# --- Google Sheets Connection ---
@st.cache_resource(ttl=3600)
def get_gsheets_client():
    try:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gsheets"],
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error("App en syncope. Merci d'oxygéner la page en la rafraichissant.")
        st.exception(e)
        st.stop()
        return None

def get_sheet_by_url(client, url, worksheet_name='Sheet1'):
    try:
        spreadsheet = client.open_by_url(url)
        return spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        st.error(f"App en syncope. Merci d'oxygéner la page en la rafraichissant.")
        st.stop()
        return None
    except Exception as e:
        st.error(f"App en syncope. Merci d'oxygéner la page en la rafraichissant.")
        st.exception(e)
        st.stop()
        return None

# --- Data Handling for Performance Records ---
@st.cache_data(ttl=60, show_spinner="Chargement des performances...")
def load_records(training_logs):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["records_sheet_url"], 'freediving_records')
    records = sheet.get_all_records()

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
        if 'comment' not in record:
            record['comment'] = ''
            updated = True
        if 'club' not in record:
            record['club'] = ''
            updated = True

        if record.get('linked_training_session_id') in {log['id'] for log in training_logs}:
            if 'event_name' in record:
                del record['event_name']
                updated = True
            if 'event_date' in record:
                del record['event_date']
                updated = True
            if 'date' in record:
                del record['date']
                updated = True
    return records

def save_records(records):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["records_sheet_url"], 'freediving_records')

    headers = ["id", "user", "entry_date", "discipline", "original_performance_str", "parsed_value", "linked_training_session_id", "comment", "club"]

    if not records:
        sheet.clear()
        sheet.update([headers])
        return

    all_keys = set()
    for record in records:
        all_keys.update(record.keys())
    
    final_headers = headers + [key for key in all_keys if key not in headers]
    
    data_to_write = [final_headers] + [[record.get(h, "") for h in final_headers] for record in records]

    sheet.clear()
    sheet.update(data_to_write)
    load_records.clear()


# --- Data Handling for User Profiles ---
@st.cache_data(ttl=60, show_spinner="Chargement des profils utilisateurs...")
def load_user_profiles():
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["user_profiles_sheet_url"], 'user_profiles')
    profiles_list = sheet.get_all_records()
    profiles = {p['user_name']: p for p in profiles_list if 'user_name' in p}

    updated = False

    for user_name, profile_data in profiles.items():
        if profile_data.get('id') is None:
            profile_data['id'] = uuid.uuid4().hex
            updated = True

        if 'club' not in profile_data:
            profile_data['club'] = ''
            updated = True

        if 'club_owner' not in profile_data:
            profile_data['club_owner'] = False
            updated = True
        
        if isinstance(profile_data.get('club_owner'), str):
            profile_data['club_owner'] = profile_data['club_owner'].lower() == 'true'
            updated = True


        for bool_field in ['anonymize_results', 'consent_ai_feedback']:
            val = profile_data.get(bool_field, False)
            if isinstance(val, str):
                profile_data[bool_field] = val.lower() == 'true'
            elif not isinstance(val, bool):
                profile_data[bool_field] = bool(val)

        for text_field in ['motivations', 'projection_3_ans', 'portrait_photo_text']:
            if text_field not in profile_data:
                profile_data[text_field] = ""
                updated = True

        if 'hashed_password' not in profile_data:
            profile_data['hashed_password'] = ''
            updated = True

        for bool_field in ['anonymize_results', 'consent_ai_feedback', 'club_owner']: # Added 'club_owner' here too for consistency
            val = profile_data.get(bool_field, False)
            if isinstance(val, str):
                profile_data[bool_field] = val.lower() == 'true'
            elif not isinstance(val, bool):
                profile_data[bool_field] = bool(val) # Ensure it's a proper boolean

    if updated:
        save_user_profiles(profiles)
        
    return profiles

def save_user_profiles(profiles):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["user_profiles_sheet_url"], 'user_profiles')

    profiles_list = list(profiles.values())
    if not profiles_list:
        sheet.clear()
        return

    # Ensure each profile has a 'user_name' key for consistency before writing
    for name, profile in profiles.items():
        profile['user_name'] = name

    expected_headers = [
        "user_name", "id", "certification", "certification_date",
        "lifras_id", "anonymize_results", "consent_ai_feedback",
        "motivations", "projection_3_ans", "portrait_photo_text",
        "hashed_password",
        "club",
        "club_owner"
    ]

    data_to_write = [expected_headers]
    for profile_data in profiles_list:
        row = []
        for header in expected_headers:
            if header == "consent_ai_feedback" or header == "anonymize_results" or header == "club_owner":
                row.append(bool(profile_data.get(header, False)))
            elif header == "certification_date":
                date_val = profile_data.get(header)
                row.append(date_val if pd.notna(date_val) else None)
            elif header == "hashed_password":
                row.append(profile_data.get(header, ''))
            elif header == "club":
                row.append(profile_data.get(header, ''))
            else:
                row.append(profile_data.get(header, ""))
        data_to_write.append(row)

    sheet.clear()
    sheet.update(data_to_write)
    load_user_profiles.clear()
    get_auth_config.clear()

# --- Data Handling for Training Logs ---
@st.cache_data(ttl=60, show_spinner="Chargement des activités...")
def load_training_log():
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["training_log_sheet_url"], 'training_log')
    logs = sheet.get_all_records()

    updated = False
    for entry in logs:
        if entry.get('id') is None:
            entry['id'] = uuid.uuid4().hex
            updated = True
        if 'club' not in entry:
            entry['club'] = ''
            updated = True

    if updated:
        save_training_log(logs)
    return logs

def save_training_log(logs):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["training_log_sheet_url"], 'training_log')

    if not logs:
        sheet.clear()
        sheet.update([["id", "date", "place", "description", "club"]])
        return

    all_keys = set()
    for log in logs:
        all_keys.update(log.keys())
    
    preferred_headers = ["id", "date", "place", "description", "club"]
    final_headers = preferred_headers + [key for key in all_keys if key not in preferred_headers]

    data_to_write = [final_headers] + [[log.get(h) for h in final_headers] for log in logs]

    sheet.clear()
    sheet.update(data_to_write)
    load_training_log.clear()

# --- Data Handling for Instructor Feedback ---
@st.cache_data(ttl=60, show_spinner="Chargement des feedbacks...")
def load_instructor_feedback():
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["instructor_feedback_sheet_url"], 'instructor_feedback')
    feedback_data = sheet.get_all_records()

    updated = False
    for entry in feedback_data:
        if entry.get('id') is None:
            entry['id'] = uuid.uuid4().hex
            updated = True
        if 'club' not in entry:
            entry['club'] = ''
            updated = True

    if updated:
        save_instructor_feedback(feedback_data)
    return feedback_data

def save_instructor_feedback(feedback_data):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["instructor_feedback_sheet_url"], 'instructor_feedback')

    if not feedback_data:
        sheet.clear()
        sheet.update([["id", "feedback_date", "diver_name", "training_session_id", "instructor_name", "feedback_text", "club"]])
        return

    all_keys = set()
    for fb in feedback_data:
        all_keys.update(fb.keys())
    
    preferred_headers = ["id", "feedback_date", "diver_name", "training_session_id", "instructor_name", "feedback_text", "club"]
    final_headers = preferred_headers + [key for key in all_keys if key not in preferred_headers]

    data_to_write = [final_headers] + [[fb.get(h) for h in final_headers] for fb in feedback_data]

    sheet.clear()
    sheet.update(data_to_write)
    load_instructor_feedback.clear()

# --- Data Handling for Freediver Wishes ---
@st.cache_data(ttl=60, show_spinner="Chargement des souhaits...")
def load_wishes():
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["freediver_wishes_sheet_url"], 'FreediverWishes')
    wishes_data = sheet.get_all_records()
    
    updated = False
    for entry in wishes_data:
        if entry.get('id') is None:
            entry['id'] = uuid.uuid4().hex
            updated = True
        if 'club' not in entry:
            entry['club'] = ''
            updated = True
            
    if updated:
        save_wishes(wishes_data)
    return wishes_data

def save_wishes(wishes_data):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["freediver_wishes_sheet_url"], 'FreediverWishes')

    if not wishes_data:
        sheet.clear()
        sheet.update([["id", "user_name", "date", "description", "club"]])
        return

    all_keys = set()
    for wish in wishes_data:
        all_keys.update(wish.keys())
    
    preferred_headers = ["id", "user_name", "date", "description", "club"]
    final_headers = preferred_headers + [key for key in all_keys if key not in preferred_headers]

    data_to_write = [final_headers] + [[wish.get(h) for h in final_headers] for wish in wishes_data]

    sheet.clear()
    sheet.update(data_to_write)
    load_wishes.clear()

# --- Data Handling for Club Profiles ---
@st.cache_data(ttl=3600*24, show_spinner="Chargement des profils de clubs...")
def load_club_profiles():
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["club_profiles_sheet_url"], 'ClubProfiles')
    club_data = sheet.get_all_records()
    
    clubs = {c['club_name']: c for c in club_data if 'club_name' in c}
    
    updated = False
    for club_name, club_profile in clubs.items():
        if club_profile.get('id') is None:
            club_profile['id'] = uuid.uuid4().hex
            updated = True
            
    if updated:
        save_club_profiles(clubs)
    return clubs

def save_club_profiles(club_profiles):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["club_profiles_sheet_url"], 'ClubProfiles')

    club_list = list(club_profiles.values())
    if not club_list:
        sheet.clear()
        sheet.update([["id", "club_name"]])
        return

    expected_headers = ["id", "club_name"]
    
    all_keys = set(expected_headers)
    for club_data in club_list:
        all_keys.update(club_data.keys())
    
    final_headers = list(expected_headers) + sorted([k for k in all_keys if k not in expected_headers])
    
    data_to_write = [final_headers]
    for club_data in club_list:
        row = []
        for header in final_headers:
            row.append(club_data.get(header, ""))
        data_to_write.append(row)

    sheet.clear()
    sheet.update(data_to_write)
    load_club_profiles.clear()

# --- Data Handling for Login Logs ---
def log_login_event(username):
    client = get_gsheets_client()
    sheet = get_sheet_by_url(client, st.secrets["gsheets"]["login_log_sheet_url"], 'LoginLogs')
    
    timestamp = datetime.now().isoformat()
    new_log_entry = [username, timestamp]

    if not sheet.get_all_values():
        sheet.append_row(["Username", "Login_Time"])
    
    sheet.append_row(new_log_entry)

# --- Authentication Config Handling ---
@st.cache_data(ttl=300, show_spinner="Authentification...")
def get_auth_config():
    """
    Loads authenticator config. Since user profiles are now in GSheets,
    this function will generate credentials based on GSheets data.
    """
    profiles = load_user_profiles()
    all_users = sorted(list(profiles.keys()))

    credentials = {'usernames': {}}

    for user_name in all_users:
        user_profile = profiles.get(user_name, {})
        stored_password_hash = user_profile.get("hashed_password")

        if not stored_password_hash:
            st.warning(f"No hashed password found for {user_name}. Using default 'changeme'. Please set a secure password via admin panel.")
            stored_password_hash = bcrypt.hashpw("changeme".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        username_key = ''.join(filter(str.isalnum, user_name)).lower()
        credentials['usernames'][username_key] = {
            "email": f"{username_key}@example.com",
            "name": user_name,
            "password": stored_password_hash
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
    """
    Displays specific tags in feedback text using Streamlit's new markdown badge syntax.
    This function processes the text and uses st.markdown to render it.
    """
    sorted_tags = sorted(FEEDBACK_TAG_BADGE_CONFIG.keys(), key=len, reverse=True)

    processed_text = text

    for tag in sorted_tags:
        config = FEEDBACK_TAG_BADGE_CONFIG[tag]
        badge_color = config.get("color", "secondary")
        badge_icon = config.get("icon", "")

        markdown_badge_color_name = badge_color if badge_color in [
            'blue', 'green', 'orange', 'red', 'violet', 'gray', 'grey',
            'primary', 'secondary', 'success', 'warning', 'danger', 'info'
        ] else 'secondary'

        badge_label = tag.replace("#apnée/", "")
        if badge_icon:
            badge_content = f"{badge_icon} {badge_label}"
        else:
            badge_content = badge_label

        markdown_badge_string = f":{markdown_badge_color_name}-badge[{badge_content}]"

        processed_text = processed_text.replace(tag, markdown_badge_string)

    st.markdown(processed_text)


# --- Login Form Display ---
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
                log_login_event(user_data['name'])
                st.rerun()
            else:
                st.error(_("login_error", lang))


def display_level_performance_tab(all_records, user_profiles, discipline_keys, lang):
    """
    Displays the aggregated performances by certification level, with a unique color for each level.
    `user_profiles` parameter should now be the already filtered profiles.
    """
    if not all_records:
        st.info(_("no_ranking_data", lang))
        return

    records_df = pd.DataFrame(all_records)

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

    merged_df = pd.merge(records_df, profiles_df, on='user', how='left')
    merged_df['certification'].fillna(_("no_certification_option", lang), inplace=True)

    merged_df = merged_df.dropna(subset=['parsed_value'])

    if merged_df.empty:
        st.info(_("no_stats_data", lang))
        return

    idx = merged_df.groupby(['user', 'discipline'])['parsed_value'].idxmax()
    if discipline_keys and is_lower_better(discipline_keys[0]):
        idx = merged_df.groupby(['user', 'discipline'])['parsed_value'].idxmin()

    best_perf_df = merged_df.loc[idx]

    cert_order = ["NB", "A1", "A2", "A3", "S4", "I1", "I2", "I3", _("no_certification_option", lang)]
    cert_colors = [
        "#D074B9",
        "#67C27F",
        "#F2B760",
        "#F28F3B",
        "#2F788C",
        "#265F70",
        "#1D4654",
        "#132D38",
        "#CCCCCC"
    ]

    sub_tab_titles = [_("disciplines." + key, lang) for key in discipline_keys]
    sub_tabs = st.tabs(sub_tab_titles)

    for i, disc_key in enumerate(discipline_keys):
        with sub_tabs[i]:
            discipline_df = best_perf_df[best_perf_df['discipline'] == disc_key]

            if discipline_df.empty:
                st.info(_("no_stats_data", lang))
                continue

            agg_df = discipline_df.groupby('certification')['parsed_value'].mean().reset_index()
            agg_df['certification'] = pd.Categorical(agg_df['certification'], categories=cert_order, ordered=True)
            agg_df = agg_df.sort_values('certification')

            if is_time_based_discipline(disc_key):
                y_axis_title = f"{_('avg_performance_col', lang)} ({_('seconds_unit', lang)})"
                agg_df['formatted_perf'] = agg_df['parsed_value'].apply(format_seconds_to_static_time)
            else:
                y_axis_title = f"{_('avg_performance_col', lang)} ({_('meters_unit', lang)})"
                agg_df['formatted_perf'] = agg_df['parsed_value'].apply(lambda x: f"{int(x)}m")

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
                height=450,
                title=f"{_('avg_performance_by_certification_header', lang)} - {_('disciplines.' + disc_key, lang)}"

            )

            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=0,
                dx=20,
                color='black',
                fontSize=14,
                fontWeight='bold'
            ).encode(
                text='formatted_perf:N'
            )

            st.altair_chart(chart + text, use_container_width=True)

def display_feedbacks_by_apneist_chart(instructor_feedback_data, user_profiles, lang):
    """
    Displays the number of feedbacks per apneist, colored by instructor.
    Below the chart, it shows a table summarizing for each instructor:
    - Apneists they have not yet evaluated.
    `instructor_feedback_data` and `user_profiles` parameters should now be the already filtered data.
    """
    if not instructor_feedback_data:
        st.info(_("no_feedback_in_log", lang))
        return

    feedback_df = pd.DataFrame(instructor_feedback_data)

    feedback_df['diver_display_name'] = feedback_df['diver_name']

    feedback_counts = feedback_df.groupby(['diver_display_name', 'instructor_name']).size().reset_index(name='count')

    unique_instructors = sorted(feedback_counts['instructor_name'].unique())

    neutral_instructor_colors = [
        "#A6CEE3",
        "#B2DF8A",
        "#FB9A99",
        "#FDBF6F",
        "#CAB2D6",
        "#8DA0CB",
        "#E78AC3",
        "#A1D99B",
        "#D9D9D9",
        "#FCCDE5",
        "#CCEBC5",
        "#BC80BD",
        "#FFED6F",
        "#FFFFB3",
        "#BEBADA",
        "#FB8072",
        "#80B1D3",
        "#FDB462",
        "#B3DE69",
        "#8FBC8F",
        "#C0C0C0",
        "#DDA0DD",
    ]

    color_domain = unique_instructors
    color_range = neutral_instructor_colors[:len(unique_instructors)]

    st.subheader(_("feedbacks_by_apneist_chart_tab_label", lang=lang))

    if not feedback_counts.empty:
        max_count = feedback_counts['count'].max()
        if max_count <= 5:
            integer_tick_values = list(range(0, max_count + 1))
        elif max_count <= 10:
            integer_tick_values = list(range(0, max_count + 1, 1))
        else:
            integer_tick_values = list(range(0, max_count + 1, max(1, max_count // 7)))

        chart = alt.Chart(feedback_counts).mark_bar().encode(
            y=alt.Y('diver_display_name:N', title=_("user_col", lang=lang), sort='-x'),
            x=alt.X('count:Q',
                    title=_("count_col", lang=lang),
                    axis=alt.Axis(
                        format=".0f",
                        values=integer_tick_values
                    )
                   ),
            color=alt.Color('instructor_name:N', title=_("instructor_name_label", lang=lang),
                            scale=alt.Scale(domain=color_domain, range=color_range)),
            tooltip=[
                alt.Tooltip('diver_display_name', title=_("user_col", lang=lang)),
                alt.Tooltip('instructor_name', title=_("instructor_name_label", lang=lang)),
                alt.Tooltip('count:Q', title=_("count_col", lang=lang), format=".0f")
            ]
        ).properties(
        ).interactive()

        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Aucune donnée de feedback à afficher dans le graphique.")


# --- Main Application Logic ---
def main_app():
    lang = st.session_state.language
    
    # Load all raw data at the very beginning
    training_log_all = load_training_log()
    all_records_all = load_records(training_log_all)
    user_profiles_all = load_user_profiles()
    instructor_feedback_all = load_instructor_feedback()
    all_wishes_all = load_wishes()
    club_profiles_all = load_club_profiles()

    current_user = st.session_state.get("name")
    is_admin_view_authorized = current_user in PRIVILEGED_USERS
    is_super_admin_view_authorized = current_user in SUPER_PRIVILEGED_USERS

    current_user_profile_data = user_profiles_all.get(current_user, {})
    current_user_club = current_user_profile_data.get("club", "")
    is_current_user_club_owner = current_user_profile_data.get("club_owner", False)

    # Initialize session state variables
    if 'selected_club_filter' not in st.session_state:
        st.session_state.selected_club_filter = current_user_club
    if 'new_club_name_buffer' not in st.session_state:
        st.session_state.new_club_name_buffer = ""
    if 'new_freediver_full_name_buffer' not in st.session_state:
        st.session_state.new_freediver_full_name_buffer = ""

    # Determine visibility of instructor section in sidebar
    is_sidebar_instructor_section_visible = False
    if current_user in user_profiles_all:
        user_cert_sidebar = user_profiles_all[current_user].get("certification")
        if user_cert_sidebar in INSTRUCTOR_CERT_LEVELS_FOR_LOGGING_FEEDBACK_SIDEBAR:
            is_sidebar_instructor_section_visible = True

    # --- Determine filtered dataframes based on selected_club_filter ---
    if is_super_admin_view_authorized and st.session_state.selected_club_filter == _("all_clubs_option", lang):
        filtered_records = all_records_all
        filtered_training_log = training_log_all
        filtered_instructor_feedback = instructor_feedback_all
        filtered_wishes = all_wishes_all
        filtered_user_profiles = user_profiles_all
    else:
        target_club = st.session_state.selected_club_filter
        
        # If a non-super-privileged user has no club, they see nothing from filtered views
        if not current_user_club and not is_super_admin_view_authorized:
            filtered_records = []
            filtered_training_log = []
            filtered_instructor_feedback = []
            filtered_wishes = []
            filtered_user_profiles = {}
        else:
            # Filtering logic for a specific club or current user's club
            filtered_records = [r for r in all_records_all if user_profiles_all.get(r['user'], {}).get('club', '') == target_club]
            filtered_training_log = [t for t in training_log_all if t.get('club', '') == target_club]
            filtered_instructor_feedback = [fb for fb in instructor_feedback_all if user_profiles_all.get(fb['diver_name'], {}).get('club', '') == target_club]
            filtered_wishes = [w for w in all_wishes_all if user_profiles_all.get(w['user_name'], {}).get('club', '') == target_club]
            filtered_user_profiles = {name: profile for name, profile in user_profiles_all.items() if profile.get('club', '') == target_club}


    with st.sidebar:
        st.info(f"Suis tes **performances** et **activités** et complète ton **profil** pour générer un **feedback personnalisé** intégrant les retours de tes encadrants 👀.")

        # --- Club Filter for SUPER_PRIVILEGED_USERS only ---
        if is_super_admin_view_authorized:
            all_club_names = sorted(list(club_profiles_all.keys()))
            if any(profile.get('club') == '' or profile.get('club') is None for profile in user_profiles_all.values()):
                all_club_names.insert(0, '')
                all_club_names = sorted(set(all_club_names), key=lambda x: (x == '', x))
            
            selected_club_for_admin_filter = st.selectbox(
                _("filter_by_club_label", lang),
                options=[_("all_clubs_option", lang)] + all_club_names,
                format_func=lambda x: x if x != '' else 'Pas de Club',
                index=([_("all_clubs_option", lang)] + all_club_names).index(st.session_state.selected_club_filter) if st.session_state.selected_club_filter in ([_("all_clubs_option", lang)] + all_club_names) else 0,
                key="admin_club_filter_sidebar",
                on_change=lambda: st.session_state.update(selected_club_filter=st.session_state.admin_club_filter_sidebar)
            )
            st.session_state.selected_club_filter = selected_club_for_admin_filter
        else:
            club_display_name = current_user_club if current_user_club else "Non défini"
            # st.success(f"Club : **{club_display_name}**")


        st.success(f"Journal de **{current_user}**", icon="📒")


        # Profile Section
        with st.expander(_("profile_header_sidebar", lang)):
            with st.form(key="profile_form_sidebar_main", border=False):
                current_certification_sidebar = current_user_profile_data.get("certification", _("no_certification_option", lang))
                cert_level_keys_from_dict_sidebar = list(TRANSLATIONS[lang]["certification_levels"].keys())
                actual_selectbox_options_sidebar = [_("no_certification_option", lang)] + cert_level_keys_from_dict_sidebar
                try:
                    current_cert_index_sidebar = actual_selectbox_options_sidebar.index(current_certification_sidebar)
                except ValueError:
                    current_cert_index_sidebar = 0

                existing_club_options = sorted(list(club_profiles_all.keys()))
                if '' not in existing_club_options:
                    existing_club_options.insert(0, '') 
                
                current_user_club_value = current_user_profile_data.get("club", "")

                try:
                    current_club_index = existing_club_options.index(current_user_club_value)
                except ValueError:
                    current_club_index = existing_club_options.index('') if '' in existing_club_options else 0

                st.selectbox(
                    _("club_label", lang),
                    options=existing_club_options,
                    format_func=lambda x: x if x != '' else 'Pas de Club',
                    index=current_club_index,
                    key="club_profile_form_sb"
                )

                st.selectbox(
                    _("certification_label", lang), options=actual_selectbox_options_sidebar,
                    index=current_cert_index_sidebar, key="certification_select_profile_form_sb"
                )

                current_cert_date_str_sidebar = current_user_profile_data.get("certification_date")
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
                    _("lifras_id_label", lang), value=current_user_profile_data.get("lifras_id", ""), key="lifras_id_profile_form_sb"
                )
                st.checkbox(
                    _("anonymize_results_label", lang),
                    value=current_user_profile_data.get("anonymize_results", False),
                    key="anonymize_profile_form_sb"
                )
                st.checkbox(
                    _("consent_ai_feedback_label", lang),
                    value=current_user_profile_data.get("consent_ai_feedback", False), # Ensure this value is consistently boolean
                    key="consent_ai_feedback_profile_form_sb"
                )
                st.text_area(
                    "Motivations à faire de l'apnée :",
                    value=current_user_profile_data.get("motivations", ""),
                    key="motivations_profile_form_sb",
                    placeholder=_("motivations_placeholder", lang), 
                    height=300
                )
                st.text_area(
                    "Où vous imaginez vous dans votre pratique de l'apnée dans 3 ans ?",
                    value=current_user_profile_data.get("projection_3_ans", ""),
                    key="projection_3_ans_profile_form_sb",
                    placeholder=_("projection_3_ans_placeholder", lang),
                    height=250
                )
                st.text_area(
                    "Texte pour le portrait photo",
                    value=current_user_profile_data.get("portrait_photo_text", ""),
                    key="portrait_photo_text_profile_form_sb",
                    placeholder=_("portrait_photo_text_placeholder", lang),
                    height=250
                )

                if st.form_submit_button(_("save_profile_button", lang)):
                    profiles_to_save = load_user_profiles() # Reload to ensure we have the latest data before modification
                    user_profile = profiles_to_save.get(current_user, {}).copy()

                    user_profile["certification"] = st.session_state.certification_select_profile_form_sb
                    user_profile["club"] = st.session_state.club_profile_form_sb.strip()
                    cert_date_val = st.session_state.cert_date_profile_form_sb
                    user_profile["certification_date"] = cert_date_val.isoformat() if cert_date_val else None
                    user_profile["lifras_id"] = st.session_state.lifras_id_profile_form_sb.strip()
                    user_profile["anonymize_results"] = st.session_state.anonymize_profile_form_sb
                    user_profile["consent_ai_feedback"] = st.session_state.consent_ai_feedback_profile_form_sb # Directly use session state value
                    user_profile["motivations"] = st.session_state.motivations_profile_form_sb.strip()
                    user_profile["projection_3_ans"] = st.session_state.projection_3_ans_profile_form_sb.strip()
                    user_profile["portrait_photo_text"] = st.session_state.portrait_photo_text_profile_form_sb.strip()

                    profiles_to_save[current_user] = user_profile

                    save_user_profiles(profiles_to_save)
                    st.success(_("profile_saved_success", lang, user=current_user))
                    st.rerun()

        # Logout Button
        if st.button(_("logout_button", lang)):
            st.session_state['authentication_status'] = False
            st.session_state['name'] = None
            if 'selected_club_filter' in st.session_state:
                del st.session_state['selected_club_filter']
            if 'new_club_name_buffer' in st.session_state:
                del st.session_state['new_club_name_buffer']
            if 'new_freediver_full_name_buffer' in st.session_state:
                del st.session_state['new_freediver_full_name_buffer']
            if 'training_place_buffer' in st.session_state:
                del st.session_state['training_place_buffer']
            if 'training_desc_buffer' in st.session_state:
                del st.session_state['training_desc_buffer']
            if 'log_perf_input_buffer' in st.session_state:
                del st.session_state['log_perf_input_buffer']
            if 'log_perf_comment_buffer' in st.session_state:
                del st.session_state['log_perf_comment_buffer']
            if 'feedback_for_user_buffer' in st.session_state:
                del st.session_state['feedback_for_user_buffer']
            if 'feedback_training_session_buffer' in st.session_state:
                del st.session_state['feedback_training_session_buffer']
            if 'feedback_text_buffer' in st.session_state:
                del st.session_state['feedback_text_buffer']
            if 'feedback_summary' in st.session_state:
                del st.session_state['feedback_summary']
            if 'wishes_summary' in st.session_state:
                del st.session_state['wishes_summary']
            
            st.rerun()

       
        # --- Sidebar Logging Forms (bottom group) ---
        # These forms are logically grouped here and use the filtered data implicitly or explicitly
        if is_sidebar_instructor_section_visible and is_admin_view_authorized:
            st.header(_("log_training_header_sidebar", lang))
            with st.form(key="log_training_form_sidebar"):
                st.date_input(_("training_date_label", lang), date.today(), key="training_date_form_key")
                st.text_input(_("training_place_label", lang), value=st.session_state.training_place_buffer, key="training_place_form_key", placeholder=_("training_place_label", lang))
                st.text_area(_("training_description_label", lang), value=st.session_state.training_desc_buffer, key="training_desc_form_key", placeholder=_("training_description_placeholder", lang), height=250)
                if st.form_submit_button(_("save_training_button", lang)):
                    desc_to_save = st.session_state.training_desc_form_key.strip()
                    place_to_save = st.session_state.training_place_form_key.strip()
                    date_to_save = st.session_state.training_date_form_key
                    if not desc_to_save:
                        st.error(_("training_description_empty_error", lang))
                    else:
                        new_training_entry = {"id": uuid.uuid4().hex, "date": date_to_save.isoformat(), "place": place_to_save, "description": desc_to_save, "club": current_user_club}
                        training_log_all.append(new_training_entry)
                        save_training_log(training_log_all)
                        st.success(_("training_session_saved_success", lang))
                        st.session_state.training_place_buffer = ""
                        st.session_state.training_desc_buffer = ""
                        st.rerun()

        st.header(_("log_performance_header", lang))
        with st.form(key="log_performance_form_sidebar_main"):
            st.write(_("logging_for", lang, user=current_user))
            if not filtered_training_log: 
                st.warning("Veuillez d'abord créer une activité.")
                st.form_submit_button(_("save_performance_button", lang), disabled=True)
            else:
                discipline_keys = ["Dynamic Bi-fins (DYN-BF)", "Static Apnea (STA)", "Dynamic No-fins (DNF)", "Depth (CWT/FIM)", "Depth (VWT/NLT)", "16x25m Speed Endurance"]
                translated_disciplines_for_display = [_("disciplines." + key, lang) for key in discipline_keys]
                training_session_options = {ts.get('id'): f"{ts.get('date')} - {ts.get('place', 'N/A')}" for ts in sorted(filtered_training_log, key=lambda x: x.get('date', '1900-01-01'), reverse=True)}
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
                    _("performance_value_label", lang), value=st.session_state.log_perf_input_buffer,
                    help=performance_help_text_perf_form, key="log_perf_input_form_widget_key", placeholder=_("performance_value", lang)
                )
                st.text_area(
                    _("performance_comment_label", lang),
                    value=st.session_state.log_perf_comment_buffer,
                    key="log_perf_comment_widget_key",
                    placeholder=_("performance_comment_placeholder", lang)
                )

                if st.form_submit_button(_("save_performance_button", lang)):
                    current_log_perf_str = st.session_state.log_perf_input_form_widget_key.strip()
                    current_log_perf_comment = st.session_state.log_perf_comment_widget_key.strip()
                    if not current_log_perf_str:
                        st.error(_("performance_value_empty_error", lang))
                    else:
                        parsed_value_for_storage = parse_static_time_to_seconds(current_log_perf_str, lang) if is_time_based_discipline(log_discipline_original_key_perf_form) else parse_distance_to_meters(current_log_perf_str, lang)
                        if parsed_value_for_storage is not None:
                            new_record = {
                                "id": uuid.uuid4().hex, "user": current_user, "entry_date": date.today().isoformat(),
                                "discipline": log_discipline_original_key_perf_form, "original_performance_str": current_log_perf_str,
                                "parsed_value": parsed_value_for_storage, "linked_training_session_id": selected_training_session_id,
                                "comment": current_log_perf_comment,
                                "club": current_user_club
                            }
                            all_records_all.append(new_record)
                            save_records(all_records_all)
                            st.success(_("performance_saved_success", lang, user=current_user))
                            st.session_state.log_perf_input_buffer = ""
                            st.session_state.log_perf_comment_buffer = ""
                            st.rerun()

        if is_sidebar_instructor_section_visible:
            st.header(_("log_feedback_header_sidebar", lang))
            with st.form(key="log_feedback_form_sidebar"):
                all_known_users_list = sorted(list(set(profile['user_name'] for profile in filtered_user_profiles.values())))
                if not all_known_users_list:
                    st.warning("Veuillez ajouter un apnéiste avant d'enregistrer un feedback.")
                else:
                    freediver_options_for_feedback = [_("select_freediver_prompt", lang)] + all_known_users_list
                    default_fb_user_idx = 0
                    try:
                        if st.session_state.feedback_for_user_buffer not in freediver_options_for_feedback:
                            st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", lang)
                        default_fb_user_idx = freediver_options_for_feedback.index(st.session_state.feedback_for_user_buffer)
                    except (ValueError, KeyError):
                        st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", lang)

                    if is_admin_view_authorized:
                        st.selectbox(
                            _("feedback_for_freediver_label", lang), options=freediver_options_for_feedback,
                            index=default_fb_user_idx, key="feedback_for_user_selectbox_key_in_form"
                        )
                    else:
                        feedback_for_user_selectbox_key_in_form = current_user

                    training_session_options_fb_form = {log['id']: f"{log.get('date', '')} - {log.get('place', '')}" for log in sorted(filtered_training_log, key=lambda x: x.get('date', '1900-01-01'), reverse=True)}
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
                    
                    st.text_area(
                        _("feedback_text_label", lang), value=st.session_state.feedback_text_buffer,
                        key="feedback_text_area_key_in_form", height=200, placeholder=_("feedback_text_area_ph", lang)
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
                                "training_session_id": sel_fb_training_id, "instructor_name": current_user, "feedback_text": sel_fb_text,
                                "club": current_user_club
                            }
                            instructor_feedback_all.append(new_feedback)
                            save_instructor_feedback(instructor_feedback_all)
                            st.success(_("feedback_saved_success", lang))
                            st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", lang)
                            st.session_state.feedback_training_session_buffer = _("select_training_prompt", lang)
                            st.session_state.feedback_text_buffer = ""
                            st.rerun()
                            
        st.header(_("wish_header_sidebar", lang))
        with st.form(key="log_wish_form_sidebar"):
            wish_description = st.text_area(_("wish_description_label", lang), key="wish_description_form_key", placeholder=_("wish_description_label_ph", lang), height=300)
            if st.form_submit_button(_("save_wish_button", lang)):
                desc_to_save = wish_description.strip()
                if not desc_to_save:
                    st.error(_("wish_description_empty_error", lang))
                else:
                    new_wish = {
                        "id": uuid.uuid4().hex,
                        "user_name": current_user,
                        "date": date.today().isoformat(),
                        "description": desc_to_save,
                        "club": current_user_club
                    }
                    all_wishes_all.append(new_wish)
                    save_wishes(all_wishes_all)
                    st.success(_("wish_saved_success", lang))
                    st.rerun()


        # --- New Club Creation Widget for SUPER_PRIVILEGED_USERS only ---
        if is_super_admin_view_authorized:
            st.header(_("new_club_header_sidebar", lang))
            with st.form(key="new_club_form_sidebar"):
                new_club_name = st.text_input(_("new_club_name_label", lang), value=st.session_state.new_club_name_buffer, key="new_club_name_input", placeholder=_("new_club_name_placeholder", lang))
                if st.form_submit_button(_("save_new_club_button", lang)):
                    name_to_save = new_club_name.strip()
                    if not name_to_save:
                        st.error(_("club_name_empty_error", lang))
                    elif name_to_save in club_profiles_all:
                        st.error(_("club_name_exists_error", lang, club_name=name_to_save))
                    else:
                        new_club_entry = {"id": uuid.uuid4().hex, "club_name": name_to_save}
                        club_profiles_all[name_to_save] = new_club_entry
                        save_club_profiles(club_profiles_all)
                        st.success(_("club_saved_success", lang, club_name=name_to_save))
                        st.session_state.new_club_name_buffer = ""
                        st.rerun()

        # --- New Freediver Widget for CLUB_OWNERS only ---
        if is_current_user_club_owner:
            st.header(_("new_freediver_header_sidebar", lang))
            if not current_user_club:
                st.warning(_("club_owner_missing_club", lang))
            else:
                with st.form(key="new_freediver_form_sidebar"):
                    full_name_input = st.text_input(
                        _("freediver_full_name_label", lang),
                        value=st.session_state.new_freediver_full_name_buffer,
                        key="new_freediver_full_name_input",
                        placeholder=_("freediver_full_name_placeholder", lang)
                    )
                    
                    cert_level_keys = list(TRANSLATIONS[lang]["certification_levels"].keys())
                    freediver_cert_options = [_("no_certification_option", lang)] + cert_level_keys
                    selected_new_freediver_cert = st.selectbox(
                        _("certification_label", lang), options=freediver_cert_options, key="new_freediver_cert_select"
                    )

                    if st.form_submit_button(_("save_new_freediver_button", lang)):
                        parts = full_name_input.strip().split()
                        if len(parts) < 2:
                            st.error(_("freediver_name_empty_error", lang))
                        else:
                            first_name = " ".join(parts[:-1]).strip()
                            last_name_initial = parts[-1][0].upper()
                            
                            new_freediver_user_name = f"{first_name} {last_name_initial}."
                            
                            if new_freediver_user_name in user_profiles_all:
                                st.error(_("freediver_exists_error", lang, user_name=new_freediver_user_name))
                            else:
                                new_profile_data = {
                                    "user_name": new_freediver_user_name,
                                    "id": uuid.uuid4().hex,
                                    "certification": selected_new_freediver_cert if selected_new_freediver_cert != _("no_certification_option", lang) else "",
                                    "certification_date": None,
                                    "lifras_id": "",
                                    "anonymize_results": False,
                                    "consent_ai_feedback": False,
                                    "motivations": "",
                                    "projection_3_ans": "",
                                    "portrait_photo_text": "",
                                    "hashed_password": bcrypt.hashpw("changeme".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                                    "club": current_user_club,
                                    "club_owner": False
                                }
                                user_profiles_all[new_freediver_user_name] = new_profile_data
                                save_user_profiles(user_profiles_all)

                                st.success(_("new_freediver_success", lang, user_name=new_freediver_user_name, club_name=current_user_club))
                                st.session_state.new_freediver_full_name_buffer = ""
                                st.rerun()

        st.caption('*Développé par Charles de Brier (2025)*')


    st.title(_("app_title", lang))

    tab_label_freedivers = _("freedivers_tab_title", lang) + " [A]"
    tab_label_main_training_log = _("training_log_tab_title", lang)
    tab_label_performances = _("performances_main_tab_title", lang)
    tab_label_main_feedback_log = _("feedback_log_tab_title", lang)
    tab_label_wishes = _("wishes_main_tab_title", lang) + " [A]"


    tabs_to_display_names = [
        tab_label_main_training_log,
        tab_label_performances,
        tab_label_main_feedback_log,
    ]
    if is_admin_view_authorized:
        tabs_to_display_names.append(tab_label_wishes)
        tabs_to_display_names.append(f"{tab_label_freedivers}")

    col_main_nav1, col_main_nav2 = st.columns(2)

    with col_main_nav1:
        current_main_tab_index = 0
        if st.session_state.current_main_tab_label in tabs_to_display_names:
            current_main_tab_index = tabs_to_display_names.index(st.session_state.current_main_tab_label)

        selected_main_tab_label = st.selectbox(
            label="Navigation Principale",
            options=tabs_to_display_names,
            index=current_main_tab_index,
            key="main_navigation_selector",
            on_change=lambda: st.session_state.update(current_main_tab_label=st.session_state.main_navigation_selector)
        )

    if selected_main_tab_label == tab_label_main_training_log:
        with st.container():
            sub_tab_definitions = [_("training_sessions_sub_tab_label", lang)]
            if is_admin_view_authorized:
                sub_tab_definitions.append(f"{_('edit_training_sessions_sub_tab_label', lang)}")
                sub_tab_definitions.append(_("training_suggestion_tab_label", lang))

            with col_main_nav2:
                selected_training_sub_tab_index = 0
                if st.session_state.selected_training_sub_tab_label in sub_tab_definitions:
                    selected_training_sub_tab_index = sub_tab_definitions.index(st.session_state.selected_training_sub_tab_label)

                selected_training_sub_tab_label = st.selectbox(
                    label="Vue des Activités",
                    options=sub_tab_definitions,
                    index=selected_training_sub_tab_index,
                    key="training_sub_tabs_selectbox",
                    on_change=lambda: st.session_state.update(selected_training_sub_tab_label=st.session_state.training_sub_tabs_selectbox)
                )

            if selected_training_sub_tab_label == _("training_sessions_sub_tab_label", lang):
                if not filtered_training_log:
                    st.info(_("no_training_sessions_logged", lang))
                else:
                    years = sorted(list(set(datetime.fromisoformat(entry['date']).year for entry in filtered_training_log if entry.get('date'))), reverse=True)
                    places = sorted(list(set(entry['place'] for entry in filtered_training_log if entry.get('place'))))
                    months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                    months_translated = [_("months." + m, lang) for m in months_en]
                    all_tags = sorted(list(FEEDBACK_TAG_BADGE_CONFIG.keys()))

                    col1_f, col2_f, col3_f, col4_f = st.columns(4)
                    with col1_f: selected_year = st.selectbox(_("filter_by_year_label", lang), [_("all_years_option", lang)] + years, key="training_year_filter")
                    with col2_f: selected_month_name = st.selectbox(_("filter_by_month_label", lang), [_("all_months_option", lang)] + months_translated, key="training_month_filter")
                    with col3_f: selected_place = st.selectbox(_("filter_by_place_label", lang), [_("all_places_option", lang)] + places, key="training_place_filter")
                    with col4_f: selected_tag = st.selectbox(_("filter_by_tag_label", lang), [_("all_tags_option", lang)] + all_tags, key="training_tag_filter")

                    display_logs = filtered_training_log
                    if selected_year != _("all_years_option", lang): display_logs = [log for log in display_logs if log.get('date') and datetime.fromisoformat(log['date']).year == selected_year]
                    if selected_month_name != _("all_months_option", lang):
                        month_number = months_translated.index(selected_month_name) + 1
                        display_logs = [log for log in display_logs if log.get('date') and datetime.fromisoformat(log['date']).month == month_number]
                    if selected_place != _("all_places_option", lang): display_logs = [log for log in display_logs if log.get('place') == selected_place]
                    if selected_tag != _("all_tags_option", lang):
                        display_logs = [log for log in display_logs if selected_tag in log.get('description', '')]

                    if not display_logs:
                        st.info("Aucune activité ne correspond aux filtres sélectionnés.")
                    else:
                        for entry in sorted(display_logs, key=lambda x: x.get('date', '1900-01-01'), reverse=True):
                            with st.expander(f"**{entry.get('date', 'N/A')} - {entry.get('place', 'N/A')}**", expanded=True):
                                with st.container(border=False):
                                    style_feedback_text(entry.get('description', _("no_description_available", lang)))

            elif is_admin_view_authorized and selected_training_sub_tab_label == _("training_suggestion_tab_label", lang):
                st.info(_("training_suggestion_intro", lang))
                if not filtered_training_log:
                    st.warning(_("no_data_for_suggestion", lang))
                else:
                    if st.button(_("generate_training_suggestion_button", lang)):
                        with st.spinner(_("generating_training_suggestion_spinner", lang)):
                            recent_sessions_desc = "\n".join([f"- {log['date']}: {log['description']}" for log in sorted(filtered_training_log, key=lambda x: x.get('date', '1900-01-01'), reverse=True)[:20]])
                            all_profiles = list(filtered_user_profiles.values())
                            cert_counts = pd.Series([p.get('certification', 'Non spécifié') for p in all_profiles]).value_counts().to_dict()
                            certs_summary_str = ", ".join([f"{count}x {cert}" for cert, count in cert_counts.items()])
                            prompts_instructions = toml.load("./prompts.toml")
                            training_instructions = prompts_instructions['training']['training_session_instructions']
                            prompt = f"""
                            Tu es un coach d'apnée créatif et expérimenté, responsable de la planification des entraînements pour un club.
                            Ta mission est de proposer une séance d'entraînement originale et stimulante pour la prochaine session en piscine, destinée à un groupe d'apnéistes de niveaux variés.
                            Évite de proposer des tables standards et répétitives. Sois créatif, mais pas trop !

                            **CONTEXTE DU CLUB :**
                            - **Composition du groupe :** {certs_summary_str}
                            - **Historique des 20 dernières séances :**
                            {recent_sessions_desc if recent_sessions_desc else "Aucune session récente."}

                            ---

                            {training_instructions}
                            """

                            try:
                                from google import genai
                                api_key = st.secrets["genai"]["key"]
                                client = genai.Client(api_key=api_key)
                                suggestion_response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                                if suggestion_response.text:
                                    style_feedback_text(suggestion_response.text)
                                else:
                                    st.error(_("suggestion_generation_error", lang))
                            except Exception as e:
                                st.error(_("api_call_error", lang, e=e))

            elif is_admin_view_authorized and selected_training_sub_tab_label == f"{_('edit_training_sessions_sub_tab_label', lang)}":
                if not filtered_training_log:
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
                        for entry in sorted(filtered_training_log, key=lambda x: x.get('date', '1900-01-01'), reverse=True)
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
                            logs_outside_filter = [log for log in training_log_all if log.get('club', '') != st.session_state.selected_club_filter and st.session_state.selected_club_filter != _("all_clubs_option", lang)]
                            
                            for row in edited_training_df.to_dict('records'):
                                if not row[_("history_delete_col_editor", lang)]:
                                    record_id = row.get("id") or uuid.uuid4().hex
                                    new_log_list.append({
                                        "id": record_id,
                                        "date": row[_("training_date_label", lang)].isoformat() if isinstance(row[_("training_date_label", lang)], date) else str(row[_("training_date_label", lang)]),
                                        "place": row[_("training_place_label", lang)],
                                        "description": row[_("training_description_label", lang)],
                                        "club": st.session_state.selected_club_filter if st.session_state.selected_club_filter != _("all_clubs_option", lang) else current_user_club
                                    })
                            save_training_log(logs_outside_filter + new_log_list)
                            st.success(_("training_log_updated_success", lang))
                            st.rerun()

    elif selected_main_tab_label == tab_label_performances:
        with st.container():
            perf_sub_tabs_labels = [
                _("personal_records_tab_label", lang),
                _("club_level_performance_tab_title", lang),
            ]

            if is_super_admin_view_authorized:
                perf_sub_tabs_labels.append(f"{_('club_performances_overview_tab_label', lang)}")

            if is_admin_view_authorized:
                perf_sub_tabs_labels.extend([
                    f"{_('performances_overview_tab_label', lang)}",
                    f"{_('edit_performances_sub_tab_label', lang)}"
                ])

            with col_main_nav2:
                selected_perf_sub_tab_index = 0
                if st.session_state.selected_perf_sub_tab_label in perf_sub_tabs_labels:
                    selected_perf_sub_tab_index = perf_sub_tabs_labels.index(st.session_state.selected_perf_sub_tab_label)

                selected_perf_sub_tab_label = st.selectbox(
                    label="Vue des Performances",
                    options=perf_sub_tabs_labels,
                    index=selected_perf_sub_tab_index,
                    key="perf_sub_tabs_selectbox",
                    on_change=lambda: st.session_state.update(selected_perf_sub_tab_label=st.session_state.perf_sub_tabs_selectbox)
                )

            if selected_perf_sub_tab_label == _("personal_records_tab_label", lang):
                user_records_for_tab = [r for r in filtered_records if r['user'] == current_user]
                if not user_records_for_tab:
                    st.info(_("no_performances_yet", lang))
                else:
                    with st.container(border=False):
                        discipline_keys = ["Dynamic Bi-fins (DYN-BF)", "Static Apnea (STA)", "Dynamic No-fins (DNF)", "Depth (CWT/FIM)", "Depth (VWT/NLT)", "16x25m Speed Endurance"]
                        pbs_tab = {}
                        for disc_key_pb_tab in discipline_keys:
                            disc_records_pb_tab = [r for r in user_records_for_tab if r['discipline'] == disc_key_pb_tab and r.get('parsed_value') is not None]
                            if not disc_records_pb_tab:
                                pbs_tab[disc_key_pb_tab] = ("N/A", "N/A", "N/A")
                                continue
                            best_record_pb_tab = min(disc_records_pb_tab, key=lambda x: x['parsed_value']) if is_lower_better(disc_key_pb_tab) else max(disc_records_pb_tab, key=lambda x: x['parsed_value'])
                            pb_value_formatted_tab = format_seconds_to_static_time(best_record_pb_tab['parsed_value']) if is_time_based_discipline(disc_key_pb_tab) else f"{int(best_record_pb_tab['parsed_value'])}m"
                            session_details = get_training_session_details(best_record_pb_tab.get('linked_training_session_id'), training_log_all)
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
                        personal_sub_tabs_objects = st.tabs(sub_tab_titles_user)

                        for i_sub_tab_user, disc_key_sub_tab_user in enumerate(discipline_keys):
                            with personal_sub_tabs_objects[i_sub_tab_user]:
                                chart_data_list = [
                                    {
                                        "Date": pd.to_datetime(get_training_session_details(r_chart.get('linked_training_session_id'), training_log_all).get('event_date')),
                                        "PerformanceValue": r_chart['parsed_value'],
                                        "Lieu": get_training_session_details(r_chart.get('linked_training_session_id'), training_log_all).get('event_name'),
                                        "Comment": r_chart.get("comment", "")
                                    }
                                    for r_chart in sorted(user_records_for_tab, key=lambda x: get_training_session_details(x.get('linked_training_session_id'), training_log_all).get('event_date') or '1900-01-01')
                                    if r_chart['discipline'] == disc_key_sub_tab_user and r_chart.get('parsed_value') is not None and get_training_session_details(r_chart.get('linked_training_session_id'), training_log_all).get('event_date')
                                ]
                                st.markdown(f"#### {_('performance_evolution_subheader', lang)}")
                                if chart_data_list:
                                    chart_df = pd.DataFrame(chart_data_list)
                                    y_axis_title = _("performance_value_label", lang)
                                    tooltip_list = ['Date:T', 'Lieu:N', alt.Tooltip('Comment:N', title=_('history_comment_col', lang))]
                                    if is_time_based_discipline(disc_key_sub_tab_user):
                                        chart_df['PerformanceValueMinutes'] = chart_df['PerformanceValue'] / 60
                                        y_axis_title += f" ({_('minutes_unit', lang)})"
                                        y_encoding_field = 'PerformanceValueMinutes:Q'
                                        tooltip_list.insert(1, alt.Tooltip('PerformanceValueMinutes:Q', title="Performance" + f" ({_('minutes_unit', lang)})", format=".2f"))
                                    else:
                                        y_axis_title += f" ({_('meters_unit', lang)})"
                                        y_encoding_field = 'PerformanceValue:Q'
                                        tooltip_list.insert(1, alt.Tooltip('PerformanceValue:Q', title="Performance" + f" ({_('meters_unit', lang)})"))
                                    chart = alt.Chart(chart_df).mark_line(point={'size': 100}).encode(
                                        x=alt.X('Date:T', title=_("history_event_date_col", lang)),
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
                                    training_session_options = {ts.get('id'): f"{ts.get('date')} - {ts.get('place', 'N/A')}" for ts in sorted(training_log_all, key=lambda x: x.get('date', '1900-01-01'), reverse=True)}
                                    training_session_options[None] = _("no_specific_session_option", lang)

                                    session_display_to_id = {v: k for k, v in training_session_options.items()}
                                    history_for_editor_display = [
                                        {
                                            "id": rec.get("id"),
                                            _("link_training_session_label", lang): training_session_options.get(rec.get("linked_training_session_id"), _("no_specific_session_option", lang)),
                                            _("history_performance_col", lang): rec.get("original_performance_str", ""),
                                            _("history_comment_col", lang): rec.get("comment", ""),
                                            _("history_delete_col_editor", lang): False
                                        }
                                        for rec in sorted(history_for_editor_raw, key=lambda x: get_training_session_details(x.get('linked_training_session_id'), training_log_all).get('event_date') or '1900-01-01', reverse=True)
                                    ]
                                    with st.form(key=f"personal_history_form_{disc_key_sub_tab_user}", border=False):
                                        performance_column_config = {}
                                        if is_time_based_discipline(disc_key_sub_tab_user):
                                            performance_column_config = st.column_config.TextColumn(label=_("history_performance_col", lang), required=True)
                                        else:
                                            performance_column_config = st.column_config.NumberColumn(
                                                label=_("history_performance_col", lang),
                                                required=True,
                                                format="%d m"
                                            )
                                        edited_df = st.data_editor(
                                            pd.DataFrame(history_for_editor_display),
                                            column_config={
                                                "id": None,
                                                _("link_training_session_label", lang): st.column_config.SelectboxColumn(options=list(training_session_options.values()), required=True),
                                                _("history_performance_col", lang): performance_column_config,
                                                _("history_comment_col", lang): st.column_config.TextColumn(label=_("history_comment_col", lang)),
                                                _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(label=_("history_delete_col_editor", lang))
                                            },
                                            hide_index=True, key=f"data_editor_{current_user}_{disc_key_sub_tab_user}"
                                        )
                                        if st.form_submit_button(_("save_history_changes_button", lang)):
                                            records_to_process = [r for r in all_records_all if not(r['user'] == current_user and r['discipline'] == disc_key_sub_tab_user)]
                                            
                                            for row in edited_df.to_dict('records'):
                                                if row[_("history_delete_col_editor", lang)]:
                                                    continue

                                                original_rec = next((r for r in all_records_all if r['id'] == row['id']), None)
                                                if original_rec:
                                                    new_perf_str = str(row[_("history_performance_col", lang)]).strip()
                                                    new_session_id = session_display_to_id.get(row[_("link_training_session_label", lang)])
                                                    parsed_val = parse_static_time_to_seconds(new_perf_str, lang) if is_time_based_discipline(disc_key_sub_tab_user) else parse_distance_to_meters(new_perf_str, lang)
                                                    if parsed_val is not None:
                                                        original_rec['original_performance_str'] = new_perf_str
                                                        original_rec['parsed_value'] = parsed_val
                                                        original_rec['linked_training_session_id'] = new_session_id
                                                        original_rec['comment'] = row.get(_("history_comment_col", lang), "").strip()
                                                    else:
                                                        st.error(f"Invalid performance format for '{new_perf_str}'")
                                                    records_to_process.append(original_rec)
                                            save_records(records_to_process)
                                            st.success(_("history_updated_success", lang))
                                            st.rerun()

            elif selected_perf_sub_tab_label == _("club_level_performance_tab_title", lang):
                display_level_performance_tab(filtered_records, filtered_user_profiles, discipline_keys, lang)

            elif is_super_admin_view_authorized and selected_perf_sub_tab_label == f"{_('club_performances_overview_tab_label', lang)}":
                if not filtered_records:
                    st.info(_("no_ranking_data", lang))
                else:
                    with st.container(border=False):
                        all_known_users_list = sorted(list(set(r['user'] for r in filtered_records).union(set(filtered_user_profiles.keys()))))
                        club_pbs = {}
                        for disc_key_club_pb in discipline_keys:
                            club_disc_records = [r for r in filtered_records if r['discipline'] == disc_key_club_pb and r.get('parsed_value') is not None]
                            if not club_disc_records:
                                club_pbs[disc_key_club_pb] = ("N/A", None, None, None)
                                continue
                            best_club_record = min(club_disc_records, key=lambda x: x['parsed_value']) if is_lower_better(disc_key_club_pb) else max(club_disc_records, key=lambda x: x['parsed_value'])
                            club_pb_value_formatted = format_seconds_to_static_time(best_club_record['parsed_value']) if is_time_based_discipline(disc_key_club_pb) else f"{int(best_club_record['parsed_value'])}m"
                            session_details = get_training_session_details(best_club_record.get('linked_training_session_id'), training_log_all)
                            club_pbs[disc_key_club_pb] = (club_pb_value_formatted, best_club_record['user'], session_details['event_name'], session_details['event_date'])
                        cols_club_pb = st.columns(len(discipline_keys))
                        for i, disc_key_club_pb_col in enumerate(discipline_keys):
                            val_club, user_club, event_name_club, event_date_club = club_pbs.get(disc_key_club_pb_col)
                            with cols_club_pb[i]:
                                metric_label_club = _("club_best_labels." + disc_key_club_pb_col, lang)
                                display_user_club = get_display_name(user_club, user_profiles_all, lang) if user_club else _("anonymous_freediver_name", lang)
                                st.metric(label=metric_label_club, value=val_club)
                                if user_club and event_date_club:
                                    st.caption(_("achieved_at_event_on_date_caption", lang, user=display_user_club, event_name=event_name_club, event_date=event_date_club))
                                elif val_club == "N/A":
                                    st.caption(_("no_record_yet_caption", lang))
                        st.markdown("")

                    ranking_sub_tab_titles = [_("disciplines." + key, lang) for key in discipline_keys]
                    ranking_sub_tabs_objects = st.tabs(ranking_sub_tab_titles)

                    for i_rank_sub_tab, selected_discipline_ranking_key in enumerate(discipline_keys):
                        with ranking_sub_tabs_objects[i_rank_sub_tab]:
                            user_pbs_for_discipline_ranking = []
                            for u_rank_tab in all_known_users_list:
                                user_specific_discipline_records_ranking = [r for r in filtered_records if r['user'] == u_rank_tab and r['discipline'] == selected_discipline_ranking_key and r.get('parsed_value') is not None]
                                if user_specific_discipline_records_ranking:
                                    best_record_for_user_ranking = min(user_specific_discipline_records_ranking, key=lambda x: x['parsed_value']) if is_lower_better(selected_discipline_ranking_key) else max(user_specific_discipline_records_ranking, key=lambda x: x['parsed_value'])
                                    session_details = get_training_session_details(best_record_for_user_ranking.get('linked_training_session_id'), training_log_all)
                                    user_pbs_for_discipline_ranking.append({
                                        "user": u_rank_tab, "parsed_value": best_record_for_user_ranking['parsed_value'],
                                        "event_date": session_details['event_date'], "event_name": session_details['event_name']
                                    })
                            sorted_rankings_tab = sorted(user_pbs_for_discipline_ranking, key=lambda x: x['parsed_value'], reverse=not is_lower_better(selected_discipline_ranking_key))
                            if not sorted_rankings_tab:
                                st.info(_("no_ranking_data", lang))
                            else:
                                ranking_table_data = [
                                    {
                                        _("rank_col", lang): rank_idx + 1,
                                        _("user_col", lang): get_display_name(rank_item['user'], user_profiles_all, lang),
                                        _("best_performance_col", lang): format_seconds_to_static_time(rank_item['parsed_value']) if is_time_based_discipline(selected_discipline_ranking_key) else f"{int(rank_item['parsed_value'])}m",
                                        _("event_col", lang): rank_item.get('event_name', "N/A"),
                                        _("date_achieved_col", lang): rank_item.get('event_date', "N/A")
                                    }
                                    for rank_idx, rank_item in enumerate(sorted_rankings_tab)
                                ]
                                st.dataframe(pd.DataFrame(ranking_table_data), use_container_width=True, hide_index=True)

            elif is_admin_view_authorized and selected_perf_sub_tab_label == f"{_('performances_overview_tab_label', lang)}":
                all_known_users_list_filtered = sorted(list(set(profile['user_name'] for profile in filtered_user_profiles.values())))
                col1_f, col2_f, col3_f = st.columns(3)
                with col1_f: filter_user_perf = st.selectbox(_("filter_by_freediver_label", lang), [_("all_freedivers_option", lang)] + all_known_users_list_filtered, key="perf_log_user_filter_overview")
                with col2_f:
                    session_options = {s['id']: f"{s['date']} - {s['place']}" for s in filtered_training_log}
                    session_options[None] = _("no_specific_session_option", lang)
                    filter_session_id_perf = st.selectbox(_("filter_by_training_session_label", lang), [_("all_sessions_option", lang)] + list(session_options.keys()), format_func=lambda x: session_options.get(x, x), key="perf_log_session_filter_overview")
                with col3_f:
                    filter_discipline_perf = st.selectbox(
                        _("filter_by_discipline_label", lang),
                        options=[_("all_disciplines_option", lang)] + discipline_keys,
                        format_func=lambda k: k if k == _("all_disciplines_option", lang) else _(f"disciplines.{k}", lang),
                        key="perf_log_discipline_filter_overview"
                    )

                display_records = filtered_records
                if filter_user_perf != _("all_freedivers_option", lang): display_records = [r for r in display_records if r['user'] == filter_user_perf]
                if filter_session_id_perf != _("all_sessions_option", lang): display_records = [r for r in display_records if r.get('linked_training_session_id') == filter_session_id_perf]
                if filter_discipline_perf != _("all_disciplines_option", lang): display_records = [r for r in display_records if r['discipline'] == filter_discipline_perf]

                display_data = [
                    {
                        _("user_col", lang): rec["user"],
                        _("history_discipline_col", lang): _(f"disciplines.{rec['discipline']}", lang),
                        _("link_training_session_label", lang): f"{get_training_session_details(rec.get('linked_training_session_id'), training_log_all)['event_date']} - {get_training_session_details(rec.get('linked_training_session_id'), training_log_all)['event_name']}",
                        _("history_performance_col", lang): rec["original_performance_str"],
                        _("history_comment_col", lang): rec.get("comment", ""),
                        _("history_entry_date_col", lang): rec["entry_date"]
                    }
                    for rec in sorted(display_records, key=lambda x: x.get('entry_date', '1900-01-01'), reverse=True)
                ]
                st.dataframe(pd.DataFrame(display_data), hide_index=True, use_container_width=True)

            elif is_admin_view_authorized and selected_perf_sub_tab_label == f"{_('edit_performances_sub_tab_label', lang)}":
                if not filtered_records:
                    st.info("No performances logged in the system for this club.")
                else:
                    all_known_users_list_filtered = sorted(list(set(profile['user_name'] for profile in filtered_user_profiles.values())))
                    training_session_options = {log['id']: f"{log.get('date')} - {log.get('place', 'N/A')}" for log in filtered_training_log}
                    training_session_options[None] = _("no_specific_session_option", lang)
                    perf_log_data = [
                        {
                            "id": rec["id"],
                            _("user_col", lang): rec["user"],
                            _("history_discipline_col", lang): _(f"disciplines.{rec['discipline']}", lang),
                            _("link_training_session_label", lang): training_session_options.get(rec.get("linked_training_session_id")),
                            _("history_performance_col", lang): rec["original_performance_str"],
                            _("history_comment_col", lang): rec.get("comment", ""),
                            _("history_delete_col_editor", lang): False
                        }
                        for rec in sorted(filtered_records, key=lambda x: x.get('entry_date', '1900-01-01'), reverse=True)
                    ]
                    session_display_to_id = {v: k for k, v in training_session_options.items()}
                    discipline_labels = [_("disciplines."+k, lang) for k in discipline_keys]
                    discipline_label_to_key = {label: key for label, key in zip(discipline_labels, discipline_keys)}

                    with st.form(key="all_performances_edit_form", border=False):
                        edited_perf_log_df = st.data_editor(
                            pd.DataFrame(perf_log_data),
                            column_config={
                                "id": None,
                                _("user_col", lang): st.column_config.SelectboxColumn(options=all_known_users_list_filtered, required=True),
                                _("history_discipline_col", lang): st.column_config.SelectboxColumn(options=discipline_labels, required=True),
                                _("link_training_session_label", lang): st.column_config.SelectboxColumn(options=list(training_session_options.values()), required=True),
                                _("history_performance_col", lang): st.column_config.TextColumn(required=True),
                                _("history_comment_col", lang): st.column_config.TextColumn(),
                                _("history_delete_col_editor", lang): st.column_config.CheckboxColumn()
                            },
                            num_rows="dynamic", hide_index=True, key="all_perf_editor", use_container_width=True
                        )
                        if st.form_submit_button(_("save_all_performances_button", lang)):
                            new_records = []
                            records_outside_filter = [r for r in all_records_all if user_profiles_all.get(r['user'], {}).get('club', '') != st.session_state.selected_club_filter and st.session_state.selected_club_filter != _("all_clubs_option", lang)]

                            for row in edited_perf_log_df.to_dict('records'):
                                if not row[_("history_delete_col_editor", lang)]:
                                    # Correction: Extract discipline, performance string and parsed value from the edited row
                                    discipline = discipline_label_to_key.get(row[_("history_discipline_col", lang)])
                                    perf_str = str(row[_("history_performance_col", lang)]).strip()
                                    parsed_val = (
                                        parse_static_time_to_seconds(perf_str, lang) if is_time_based_discipline(discipline)
                                        else parse_distance_to_meters(perf_str, lang)
                                    )
                                    if parsed_val is None:
                                        st.error(f"Erreur de format pour la performance '{perf_str}' dans la discipline '{row[_('history_discipline_col', lang)]}'.")
                                        continue # Skip this row if parsing fails

                                    diver_club = user_profiles_all.get(row[_("user_col", lang)], {}).get('club', '')
                                    original_rec = next((r for r in filtered_records if r.get('id') == row.get('id')), None) # Find original to retain entry_date if exists

                                    new_records.append({
                                        "id": row.get("id") or uuid.uuid4().hex,
                                        "user": row[_("user_col", lang)],
                                        "discipline": discipline,
                                        "linked_training_session_id": session_display_to_id.get(row[_("link_training_session_label", lang)]),
                                        "original_performance_str": perf_str,
                                        "parsed_value": parsed_val,
                                        "entry_date": original_rec.get('entry_date', date.today().isoformat()) if original_rec else date.today().isoformat(),
                                        "comment": row.get(_("history_comment_col", lang), "").strip(),
                                        "club": diver_club
                                    })
                            save_records(records_outside_filter + [r for r in new_records if r is not None])
                            st.success(_("all_performances_updated_success", lang))
                            st.rerun()

    elif selected_main_tab_label == tab_label_main_feedback_log:
        with st.container():
            my_feedback_sub_tab_label = _("my_feedback_tab_label", lang)

            feedback_sub_tabs_labels = [my_feedback_sub_tab_label]
            if is_admin_view_authorized:
                feedback_sub_tabs_labels.append(f"{_('feedbacks_overview_tab_label', lang)}")
                feedback_sub_tabs_labels.append(f"{_('edit_feedbacks_sub_tab_label', lang)}")
                feedback_sub_tabs_labels.append(f"{_('feedbacks_by_apneist_chart_tab_label', lang)}")

            with col_main_nav2:
                selected_feedback_sub_tab_index = 0
                if st.session_state.selected_feedback_sub_tab_label in feedback_sub_tabs_labels:
                    selected_feedback_sub_tab_index = feedback_sub_tabs_labels.index(st.session_state.selected_feedback_sub_tab_label)

                selected_feedback_sub_tab_label = st.selectbox(
                    label="Vue des Feedbacks",
                    options=feedback_sub_tabs_labels,
                    index=selected_feedback_sub_tab_index,
                    key="feedback_sub_tabs_selectbox",
                    on_change=lambda: st.session_state.update(selected_feedback_sub_tab_label=st.session_state.feedback_sub_tabs_selectbox)
                )

            if selected_feedback_sub_tab_label == my_feedback_sub_tab_label:
                user_feedback = [fb for fb in filtered_instructor_feedback if fb.get('diver_name') == current_user]
                fresh_user_profiles = filtered_user_profiles
                user_profile_data = fresh_user_profiles.get(current_user, {})
                has_ai_consent = user_profile_data.get("consent_ai_feedback", False)

                num_feedbacks = len(user_feedback)
                st.info(f"Tu as reçu **{num_feedbacks}** feedback(s).")
                

                if not has_ai_consent:
                    st.warning(_("consent_ai_feedback_missing", lang))

                if has_ai_consent:

                    st.info('''
                            Le résumé des feedbacks est généré par une intelligence artificielle et **peut dès lors contenir des erreurs ou des imprécisions**. 
                            Il peut même halluciner comme on dit ;). Mais on a fait de notre mieux pour qu'il suive le droit chemin ! 
                            Nous lui avons indiqué de se comporter comme un **coach d'apnée certifié Adeps**, bienveillant, clair et constructif.
                            Il a également reçu des instructions spécifiques sur les niveaux de la Lifras, ainsi que des **éléments de théorie** issus de coachs d'apnée. 

                            Le feedback IA est dépendant du **nombre de feedbacks laissés par tes encadrants** : plus ceux-ci sont nombreux, plus le feedback IA sera pertinent.
                            
                            Aussi, il est important que les données dans la section **Mon Profil** de la barre latérale soient à jour si tu souhaites augmenter la pertinence du feedback IA.
                            N'oubliez pas de sauvegarder votre profil ! 

                            Dans tous les cas, utilisez-le comme un **guide général** et n\'hésitez pas à **consulter vos encadrants** pour des conseils personnalisés, ou si vous avez des questions. 

                            ''')

                    if not user_feedback:
                        st.info(_("no_feedback_to_summarize", lang))

                    if st.button(_("generate_feedback_summary_button", lang)):
                        with st.spinner("Génération du résumé..."):
                            all_feedback_text = "\n".join([f"- {fb['feedback_text']}" for fb in user_feedback])

                            prompts_instructions = toml.load("./prompts.toml")
                            adeps_coaching_instructions = prompts_instructions['feedback']['adeps_coaching_instructions']
                            huron_spirit = prompts_instructions['feedback']['huron_spirit']
                            comparatif_brevets = prompts_instructions['feedback']['comparatif_brevets']
                            motivations_text = user_profile_data.get("motivations", "")
                            objectifs_text = user_profile_data.get("projection_3_ans", "")
                            vision_text = user_profile_data.get("portrait_photo_text", "")

                            prompt = f"""
                                Tu es un coach d'apnée certifié Adeps, tel que décrit dans le document suivant : {adeps_coaching_instructions}. 
                                Ta mission est d’analyser une série de feedbacks reçus par un apnéiste, provenant d’instructeurs et d’autres pratiquants. 
                                Sur base de ces observations, tu dois rédiger un **résumé constructif**, **bienveillant**, **factuel** et **motivant**, destiné à cet apnéiste. 
                                Ce résumé doit contenir **maximum 10 phrases**, peut contenir plusieurs paragraphes, sans liste à puces, et couvrir l’ensemble de la pratique : **technique**, **sécurité**, **relaxation**, **état d’esprit**, **progression**, **motivation**.

                                Avant d’écrire, prends en compte :
                                - Le niveau actuel de l’apnéiste : {user_profile_data.get('certification', 'Non spécifié')}.
                                - Ses motivations à pratiquer l’apnée : {motivations_text}.
                                - Ses objectifs de progression : {objectifs_text}.
                                - Sa vision personnelle de l’apnée : {vision_text}.
                                - Les exigences de la Lifras pour chaque niveau d’apnée, disponibles ici : {comparatif_brevets}.
                                - Des éléments de théorie issus de l’approche du coach Huron : {huron_spirit}.

                                **Ne mentionne pas explicitement d’évènements potentiellement traumatisants ou sensibles** (problèmes de santé, expériences difficiles, etc.). Adopte une posture de recul, en vue d’ensemble (« bird-eye view »).

                                Les feedbacks à analyser sont les suivants :
                                {all_feedback_text}

                                Ta synthèse doit être claire, fluide et adaptée au niveau réel de l’apnéiste. 
                                Mets en évidence les **recommandations clés en gras**, sans surcharger le texte. Relis-toi attentivement pour t’assurer que toutes les consignes ont bien été respectées. Modifie ton texte si nécessaire.
                                """

                            try:
                                from google import genai
                                api_key = st.secrets["genai"]["key"]
                                client = genai.Client(api_key=api_key)
                                summary_text = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                                st.session_state['feedback_summary'] = summary_text.text
                            except Exception as e:
                                st.error(f"Erreur lors de la génération du résumé : {e}")
                                st.session_state['feedback_summary'] = None

                if 'feedback_summary' in st.session_state and st.session_state.feedback_summary:
                    st.markdown(st.session_state['feedback_summary'])

                st.subheader(_("my_self_feedbacks_header", lang))

                self_feedbacks = [
                    fb for fb in filtered_instructor_feedback
                    if fb.get('diver_name') == current_user and fb.get('instructor_name') == current_user
                ]

                if not self_feedbacks:
                    st.info(_("no_self_feedbacks_yet", lang))
                else:
                    table_data = []
                    for fb in self_feedbacks:
                        session_details = get_training_session_details(fb.get("training_session_id"), training_log_all)
                        event_date_str = session_details.get('event_date')
                        
                        sort_date = datetime.min
                        if event_date_str:
                            try:
                                sort_date = datetime.fromisoformat(event_date_str)
                            except (ValueError, TypeError):
                                pass
                            
                        table_data.append({
                            _("self_feedback_event_col", lang): session_details.get('event_name', _("no_specific_session_option", lang)),
                            _("self_feedback_date_col", lang): event_date_str if event_date_str else "N/A",
                            _("self_feedback_text_col", lang): fb.get('feedback_text', ''),
                            "sort_key": sort_date
                        })

                    sorted_data = sorted(table_data, key=lambda x: x["sort_key"], reverse=True)

                    for row in sorted_data:
                        del row["sort_key"]

                    df_display = pd.DataFrame(sorted_data)
                    st.dataframe(df_display, hide_index=True, use_container_width=True)

            elif is_admin_view_authorized and selected_feedback_sub_tab_label == f"{_('feedbacks_overview_tab_label', lang)}":
                all_known_users_list_filtered = sorted(list(set(profile['user_name'] for profile in filtered_user_profiles.values())))
                col1_f, col2_f, col3_f = st.columns(3)
                with col1_f:
                    filter_user = st.selectbox(_("filter_by_freediver_label", lang), [_("all_freedivers_option", lang)] + all_known_users_list_filtered, key="fb_overview_user")
                with col2_f:
                    session_options = {s['id']: f"{s.get('date', 'N/A')} - {s.get('place', 'N/A')}" for s in filtered_training_log}
                    session_options[None] = _("no_specific_session_option", lang)
                    filter_session_id = st.selectbox(_("filter_by_training_session_label", lang), [_("all_sessions_option", lang)] + list(session_options.keys()), format_func=lambda x: session_options.get(x, x), key="fb_overview_session")
                with col3_f:
                    instructors = sorted(list(set(fb['instructor_name'] for fb in filtered_instructor_feedback)))
                    filter_instructor = st.selectbox(_("filter_by_instructor_label", lang), [_("all_instructors_option", lang)] + instructors, key="fb_overview_instructor")

                display_feedbacks = filtered_instructor_feedback
                if filter_user != _("all_freedivers_option", lang):
                    display_feedbacks = [f for f in display_feedbacks if f['diver_name'] == filter_user]
                if filter_session_id != _("all_sessions_option", lang):
                    display_feedbacks = [f for f in display_feedbacks if f.get('training_session_id') == filter_session_id]
                if filter_instructor != _("all_instructors_option", lang):
                    display_feedbacks = [f for f in display_feedbacks if f['instructor_name'] == filter_instructor]

                if not display_feedbacks:
                    st.info(_("no_feedbacks_match_filters", lang))
                else:
                    for fb in sorted(display_feedbacks, key=lambda x: x.get('feedback_date', '1900-01-01'), reverse=True):
                        session_details = get_training_session_details(fb.get("training_session_id"), training_log_all)
                        display_date = session_details['event_date'] or _('no_specific_session_option', lang)
                        st.markdown(f"**{fb['diver_name']} par {fb['instructor_name']} à {session_details['event_name']} le {display_date}**")
                        with st.container(border=False):
                            style_feedback_text(fb['feedback_text'])
                        st.markdown("")

            elif is_admin_view_authorized and selected_feedback_sub_tab_label == f"{_('edit_feedbacks_sub_tab_label', lang)}":
                if not filtered_instructor_feedback:
                    st.info(_("no_feedback_in_log", lang))
                else:
                    with st.form(key="feedback_log_edit_form", border=False):
                        all_known_users_list_filtered = sorted(list(set(profile['user_name'] for profile in filtered_user_profiles.values())))
                        session_options = {s['id']: f"{s.get('date', 'N/A')} - {s.get('place', 'N/A')}" for s in filtered_training_log}
                        session_options[None] = _("no_specific_session_option", lang)

                        feedback_df_data = []
                        for fb in filtered_instructor_feedback:
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
                                _("feedback_for_freediver_label", lang): st.column_config.SelectboxColumn(options=all_known_users_list_filtered, required=True),
                                _("instructor_name_label", lang): st.column_config.SelectboxColumn(options=all_known_users_list_filtered, required=True),
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
                            feedback_outside_filter = [fb for fb in instructor_feedback_all if user_profiles_all.get(fb['diver_name'], {}).get('club', '') != st.session_state.selected_club_filter and st.session_state.selected_club_filter != _("all_clubs_option", lang)]

                            for row in edited_feedback_df.to_dict('records'):
                                if not row[_("history_delete_col_editor", lang)]:
                                    date_val = row[_("feedback_date_col", lang)]
                                    diver_club = user_profiles_all.get(row[_("feedback_for_freediver_label", lang)], {}).get('club', '')
                                    new_feedback_list.append({
                                        "id": row.get("id") or uuid.uuid4().hex,
                                        "feedback_date": date_val.isoformat() if isinstance(date_val, date) else str(date_val),
                                        "diver_name": row[_("feedback_for_freediver_label", lang)],
                                        "instructor_name": row[_("instructor_name_label", lang)],
                                        "feedback_text": row[_("feedback_text_label", lang)].strip(),
                                        "training_session_id": session_display_to_id.get(row[_("link_training_session_label", lang)]),
                                        "club": diver_club
                                    })
                            save_instructor_feedback(feedback_outside_filter + new_feedback_list)
                            st.success(_("feedback_log_updated_success", lang))
                            st.rerun()

            elif is_admin_view_authorized and selected_feedback_sub_tab_label == f"{_('feedbacks_by_apneist_chart_tab_label', lang)}":
                display_feedbacks_by_apneist_chart(filtered_instructor_feedback, filtered_user_profiles, lang)

    elif is_admin_view_authorized and selected_main_tab_label == tab_label_wishes:
        with st.container():
            wishes_sub_tabs_labels = [
                _("wishes_log_sub_tab_label", lang),
                _("edit_wishes_sub_tab_label", lang),    
                _("wishes_summary_sub_tab_label", lang)
            ]

            with col_main_nav2:
                selected_wishes_sub_tab_index = 0
                if st.session_state.selected_wishes_sub_tab_label in wishes_sub_tabs_labels:
                    selected_wishes_sub_tab_index = wishes_sub_tabs_labels.index(st.session_state.selected_wishes_sub_tab_label)

                selected_wishes_sub_tab_label = st.selectbox(
                    label="Vue des Souhaits",
                    options=wishes_sub_tabs_labels,
                    index=selected_wishes_sub_tab_index,
                    key="wishes_sub_tabs_selectbox",
                    on_change=lambda: st.session_state.update(selected_wishes_sub_tab_label=st.session_state.wishes_sub_tabs_selectbox)
                )

            if 'selected_wishes_sub_tab_label' not in st.session_state:
                st.session_state.selected_wishes_sub_tab_label = TRANSLATIONS['fr']['wishes_log_sub_tab_label']


            if selected_wishes_sub_tab_label == _("wishes_log_sub_tab_label", lang):
                if not filtered_wishes:
                    st.info(_("no_wishes_logged", lang))
                else:
                    for wish in sorted(filtered_wishes, key=lambda x: x.get('date', '1900-01-01'), reverse=True):
                        display_user = get_display_name(wish.get('user_name'), user_profiles_all, lang)
                        
                        expander_label = _("wish_by", user=display_user, date=wish.get('date', 'N/A'))
                        
                        with st.expander(f"**{expander_label}**", expanded=True):
                            with st.container(border=False):
                                st.markdown(wish.get('description', ''))

            elif selected_wishes_sub_tab_label == _("wishes_summary_sub_tab_label", lang):
                if not filtered_wishes:
                    st.info(_("no_wishes_to_summarize", lang))
                else:
                    if st.button(_("generate_wishes_summary_button", lang)):
                        with st.spinner("Génération de la synthèse des souhaits..."):
                            all_wishes_text = "\n".join([f"- Souhait de {get_display_name(w.get('user_name'), user_profiles_all, lang)}: {w.get('description')}" for w in filtered_wishes])
                            
                            prompt = f"""
                            Tu es un assistant pour un club d'apnée.
                            Ta mission est d'analyser et de synthétiser une liste de souhaits et suggestions émises par les membres du club.
                            Produis un résumé clair, concis et structuré qui met en évidence les suggestions récurrentes et pertinentes.
                            Le but est de fournir aux encadrants du club un aperçu actionnable pour améliorer l'expérience des membres.

                            Voici la liste des souhaits à analyser :
                            {all_wishes_text}

                            Adopte un ton neutre et informatif.
                            Sois concis.
                            S'il y a des souhaits qui citent nommément un encadrant, tu peux le rapporter ainsi. Le but est de s'améliorer.
                            Ne fais pas de liste à puces.
                            Ne mentionne pas le nombre de fois qu'un souhait a été exprimé.
                            Ne fais pas de recommandations, ne propose pas de solutions.
                            Concentre-toi uniquement sur les souhaits exprimés.

                            Ton résumé doit être présenté sous forme de tableaux. 
                            Il faut deux tableaux :
                            1) Les points positifs
                            2) Les points négatifs

                            Chaque tableau doit comprendre deux colonnes: 
                            1) Une colonne avec le point positif ou négatif, récurrent ou unique.
                            2) Une colonne qui reprend des examples de souhaits associés.

                            Dans chaque tableau, il me faut un maximum de 5 lignes. 
                            Il faut donc que tu regroupes les souhaits et leurs exemples en thèmes simliaires. 
                            """
                            try:
                                from google import genai
                                api_key = st.secrets["genai"]["key"]
                                client = genai.Client(api_key=api_key)
                                summary_text = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
                                st.session_state['wishes_summary'] = summary_text.text
                            except Exception as e:
                                st.error(f"Erreur lors de la génération de la synthèse des souhaits : {e}")
                                st.session_state['wishes_summary'] = "Impossible de générer le résumé."

                if 'wishes_summary' in st.session_state and st.session_state.wishes_summary:
                    st.markdown(st.session_state['wishes_summary'])

            elif selected_wishes_sub_tab_label == _("edit_wishes_sub_tab_label", lang):
                if not filtered_wishes:
                    st.info(_("no_wishes_logged", lang))
                else:
                    with st.form(key="wishes_edit_form", border=False):
                        all_known_users_list_filtered = sorted(list(set(profile['user_name'] for profile in filtered_user_profiles.values())))
                        
                        wishes_df_data = []
                        for wish in filtered_wishes:
                            dt_obj = None
                            try:
                                dt_obj = date.fromisoformat(wish.get("date"))
                            except (ValueError, TypeError):
                                pass
                            wishes_df_data.append({
                                "id": wish["id"],
                                _("wish_date_col", lang): dt_obj,
                                _("user_col", lang): wish["user_name"],
                                _("wish_description_label", lang): wish["description"],
                                _("history_delete_col_editor", lang): False
                            })

                        wishes_df = pd.DataFrame(wishes_df_data)

                        edited_wishes_df = st.data_editor(
                            wishes_df,
                            column_config={
                                "id": None,
                                _("wish_date_col", lang): st.column_config.DateColumn(required=True, format="YYYY-MM-DD"),
                                _("user_col", lang): st.column_config.SelectboxColumn(options=all_known_users_list_filtered, required=True),
                                _("wish_description_label", lang): st.column_config.TextColumn(required=True),
                                _("history_delete_col_editor", lang): st.column_config.CheckboxColumn()
                            },
                            num_rows="dynamic",
                            hide_index=True,
                            key="wishes_editor",
                            use_container_width=True
                        )

                        if st.form_submit_button(_("save_wishes_changes_button", lang)):
                            new_wishes_list = []
                            wishes_outside_filter = [w for w in all_wishes_all if user_profiles_all.get(w['user_name'], {}).get('club', '') != st.session_state.selected_club_filter and st.session_state.selected_club_filter != _("all_clubs_option", lang)]

                            for row in edited_wishes_df.to_dict('records'):
                                if not row[_("history_delete_col_editor", lang)]:
                                    date_val = row[_("wish_date_col", lang)]
                                    user_club_for_wish = user_profiles_all.get(row[_("user_col", lang)], {}).get('club', '')
                                    new_wishes_list.append({
                                        "id": row.get("id") or uuid.uuid4().hex,
                                        "date": date_val.isoformat() if isinstance(date_val, date) else str(date_val),
                                        "user_name": row[_("user_col", lang)],
                                        "description": row[_("wish_description_label", lang)].strip(),
                                        "club": user_club_for_wish
                                    })
                            save_wishes(wishes_outside_filter + new_wishes_list)
                            st.success(_("wishes_updated_success", lang))
                            st.rerun()

    elif is_admin_view_authorized and selected_main_tab_label == tab_label_freedivers:
        with st.container():
            freedivers_sub_tab_labels = [
                _("journal_freedivers_tab_label", lang),
                _("edit_freedivers_sub_tab_label", lang),
                _("freediver_certification_chart_tab_label", lang)
            ]

            with col_main_nav2:
                selected_freedivers_sub_tab_index = 0
                if st.session_state.selected_freedivers_sub_tab_label in freedivers_sub_tab_labels:
                    selected_freedivers_sub_tab_index = freedivers_sub_tab_labels.index(st.session_state.selected_freedivers_sub_tab_label)

                selected_freedivers_sub_tab_label = st.selectbox(
                    label="Vue des Apnéistes",
                    options=freedivers_sub_tab_labels,
                    index=selected_freedivers_sub_tab_index,
                    key="freedivers_sub_tabs_selectbox",
                    on_change=lambda: st.session_state.update(selected_freedivers_sub_tab_label=st.session_state.freedivers_sub_tabs_selectbox)
                )

            if selected_freedivers_sub_tab_label == freedivers_sub_tab_labels[0]:
                all_known_users_sorted = sorted(list(filtered_user_profiles.keys()))
                if not all_known_users_sorted:
                    st.info(_("no_users_yet", lang))
                else:
                    cols = st.columns(2)
                    current_col = 0

                    for user_name_display in all_known_users_sorted:
                        with cols[current_col]:
                            profile_data_display = filtered_user_profiles.get(user_name_display, {})
                            with st.container(border=True):
                                with st.expander(f"**{user_name_display}** : {profile_data_display.get('certification', _('no_certification_option', lang))} depuis le {profile_data_display.get('certification_date', 'N/A')}", expanded=True):
                                    st.markdown(f"**Motivations :**<br>{profile_data_display.get('motivations', 'N/A')}", unsafe_allow_html=True)
                                    st.markdown(f"**Projections :**<br>{profile_data_display.get('projection_3_ans', 'N/A')}", unsafe_allow_html=True)
                                    st.markdown(f"**Portrait :**<br>{profile_data_display.get('portrait_photo_text', 'N/A')}", unsafe_allow_html=True)

                        current_col = 1 - current_col

            elif selected_freedivers_sub_tab_label == freedivers_sub_tab_labels[1]:
                all_known_users_list_filtered = sorted(list(set(profile['user_name'] for profile in filtered_user_profiles.values())))
                freedivers_data_for_editor = []
                for user_name in all_known_users_list_filtered:
                    profile = filtered_user_profiles.get(user_name, {})
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
                        _("anonymize_results_col_editor", lang): profile.get("anonymize_results", False),
                        _("club_label", lang): profile.get("club", ""),
                        "club_owner": profile.get("club_owner", False)
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
                            _("anonymize_results_col_editor", lang): st.column_config.CheckboxColumn(),
                            _("club_label", lang): st.column_config.TextColumn(),
                            "club_owner": st.column_config.CheckboxColumn(label="Propriétaire de Club ?", help="Cochez si cet utilisateur est un propriétaire de club.")
                        },
                        key="freedivers_data_editor", num_rows="dynamic", hide_index=True
                    )
                    if st.form_submit_button(_("save_freedivers_changes_button", lang)):
                        edited_rows = edited_freedivers_df.to_dict('records')

                        final_profiles = load_user_profiles()
                        new_names_from_editor = {row[_("freediver_name_col_editor", lang)].strip() for row in edited_rows}

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

                                profile_data = final_profiles.get(original_name, {}).copy()

                                cert_date_val = row[_("certification_date_col_editor", lang)]
                                profile_data["certification"] = row[_("certification_col_editor", lang)]
                                profile_data["certification_date"] = cert_date_val.isoformat() if pd.notna(cert_date_val) and isinstance(cert_date_val, (date, datetime)) else None
                                profile_data["lifras_id"] = str(row[_("lifras_id_col_editor", lang)]).strip() if pd.notna(row[_("lifras_id_col_editor", lang)]) else ""
                                profile_data["anonymize_results"] = bool(row[_("anonymize_results_col_editor", lang)])
                                profile_data["consent_ai_feedback"] = bool(profile.get("consent_ai_feedback", False))
                                profile_data["club"] = row[_("club_label", lang)].strip()
                                profile_data["club_owner"] = bool(row["club_owner"])

                                new_password_for_hash = row.get(_("set_reset_password_col_editor", lang))
                                if new_password_for_hash:
                                    profile_data["hashed_password"] = bcrypt.hashpw(new_password_for_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                                if original_name and original_name != new_name:
                                    name_map[original_name] = new_name
                                    if original_name in final_profiles:
                                        del final_profiles[original_name]

                                final_profiles[new_name] = profile_data

                            if name_map:
                                for rec in all_records_all:
                                    rec["user"] = name_map.get(rec.get("user"), rec.get("user"))
                                for fb in instructor_feedback_all:
                                    fb["diver_name"] = name_map.get(fb.get("diver_name"), fb.get("diver_name"))
                                    fb["instructor_name"] = name_map.get(fb.get("instructor_name"), fb.get("instructor_name"))
                                for w in all_wishes_all:
                                    w["user_name"] = name_map.get(w.get("user_name"), w.get("user_name"))
                                for t_log in training_log_all:
                                    pass

                                if st.session_state.get("name") in name_map:
                                    st.session_state["name"] = name_map[st.session_state.get("name")]

                            save_user_profiles(final_profiles)
                            save_records(all_records_all)
                            save_instructor_feedback(instructor_feedback_all)
                            save_wishes(all_wishes_all)
                            st.success(_("freedivers_updated_success", lang))
                            st.rerun()

            elif selected_freedivers_sub_tab_label == _("freediver_certification_chart_tab_label", lang):

                all_known_users_list_filtered = sorted(list(set(profile['user_name'] for profile in filtered_user_profiles.values())))
                freedivers_data_for_chart = []
                for user_name in all_known_users_list_filtered:
                    profile = filtered_user_profiles.get(user_name, {})
                    freedivers_data_for_chart.append({
                        _("certification_col_editor", lang): profile.get("certification", _("no_certification_option", lang)),
                    })
                
                cert_order = ['NB', 'A1', 'A2', 'A3', 'S4', 'I1', 'I2', 'I3']
                counts_df = (pd.DataFrame(freedivers_data_for_chart)[_("certification_col_editor", lang)]
                                .value_counts()
                                .reindex(cert_order)
                                .fillna(0)
                                .astype(int)
                                .reset_index()
                                )
                counts_df.columns = ['Niveau', 'Nombre']

                cert_colors = [
                    "#D074B9", "#67C27F", "#F2B760", "#F28F3B", "#2F788C",
                    "#265F70", "#1D4654", "#132D38", "#CCCCCC"
                ]
                chart = alt.Chart(counts_df).mark_bar().encode(
                    y=alt.Y('Niveau:N', title="Niveau de Brevet", sort=cert_order[::-1] ),
                    x=alt.X('Nombre:Q', title="Nombre d'apnéistes"),
                    color=alt.Color('Niveau:N', scale=alt.Scale(domain=cert_order, range=cert_colors), legend=None),
                    tooltip=[alt.Tooltip('Niveau', title="Niveau"), alt.Tooltip('Nombre', title="Total")]
                )
                text = chart.mark_text(align='left', baseline='middle', dx=5, color='black', fontSize=12).encode(text='Nombre:Q')
                final_chart = (chart + text).properties(title="Nombre d'apnéistes par niveau de brevet", height=300)
                st.altair_chart(final_chart, use_container_width=True)

                profiles_df_all = pd.DataFrame(filtered_user_profiles.values())
                
                certification_order = ["I3", "I2", "I1", "S4", "A3", "A2", "A1", "NB", _("no_certification_option", lang)]

                freedivers_by_cert = {cert: [] for cert in certification_order}

                for index, row in profiles_df_all.iterrows():
                    cert = row.get('certification', _("no_certification_option", lang))
                    user_name = row.get('user_name')
                    if user_name:
                        freedivers_by_cert[cert].append(user_name)
                
                max_freedivers = 0
                for cert in certification_order:
                    if len(freedivers_by_cert[cert]) > max_freedivers:
                        max_freedivers = len(freedivers_by_cert[cert])

                table_data = []
                for i in range(max_freedivers):
                    row_data = {}
                    for cert in certification_order:
                        if i < len(freedivers_by_cert[cert]):
                            row_data[cert] = freedivers_by_cert[cert][i]
                        else:
                            row_data[cert] = ""
                    table_data.append(row_data)

                freediver_cert_table_df = pd.DataFrame(table_data)

                if not freediver_cert_table_df.empty:
                    st.dataframe(freediver_cert_table_df, hide_index=True, use_container_width=True)
                else:
                    st.info(_("no_users_yet", lang))


# --- Main Execution ---
def main():
    """Main function to run the Streamlit app."""
    if 'language' not in st.session_state:
        st.session_state.language = 'fr'
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = None

    if 'current_main_tab_label' not in st.session_state:
        st.session_state.current_main_tab_label = TRANSLATIONS['fr']['training_log_tab_title']

    if 'selected_training_sub_tab_label' not in st.session_state:
        st.session_state.selected_training_sub_tab_label = TRANSLATIONS['fr']['training_sessions_sub_tab_label']
    if 'selected_perf_sub_tab_label' not in st.session_state:
        st.session_state.selected_perf_sub_tab_label = TRANSLATIONS['fr']['personal_records_tab_label']
    if 'selected_personal_sub_sub_tab_label' not in st.session_state:
        st.session_state.selected_personal_sub_sub_tab_label = TRANSLATIONS['fr']['disciplines']['Static Apnea (STA)']
    if 'selected_ranking_sub_sub_tab_label' not in st.session_state:
        st.session_state.selected_ranking_sub_sub_tab_label = TRANSLATIONS['fr']['disciplines']['Static Apnea (STA)']
    if 'selected_feedback_sub_tab_label' not in st.session_state:
        st.session_state.selected_feedback_sub_tab_label = TRANSLATIONS['fr']['my_feedback_tab_label']
    if 'selected_freedivers_sub_tab_label' not in st.session_state:
        st.session_state.selected_freedivers_sub_tab_label = TRANSLATIONS['fr']['journal_freedivers_tab_label']
    if 'selected_wishes_sub_tab_label' not in st.session_state:
        st.session_state.selected_wishes_sub_tab_label = TRANSLATIONS['fr']['wishes_log_sub_tab_label']

    if 'training_place_buffer' not in st.session_state:
        st.session_state.training_place_buffer = ""
    if 'training_desc_buffer' not in st.session_state:
        st.session_state.training_desc_buffer = ""
    if 'log_perf_input_buffer' not in st.session_state:
        st.session_state.log_perf_input_buffer = ""
    if 'log_perf_comment_buffer' not in st.session_state:
        st.session_state.log_perf_comment_buffer = ""
    if 'feedback_for_user_buffer' not in st.session_state:
        st.session_state.feedback_for_user_buffer = ""
    if 'feedback_training_session_buffer' not in st.session_state:
        st.session_state.feedback_training_session_buffer = ""
    if 'feedback_text_buffer' not in st.session_state:
        st.session_state.feedback_text_buffer = ""
    if 'feedback_summary' not in st.session_state:
        st.session_state.feedback_summary = None
    if 'wishes_summary' not in st.session_state:
        st.session_state.wishes_summary = None
    if 'new_club_name_buffer' not in st.session_state:
        st.session_state.new_club_name_buffer = ""
    if 'new_freediver_full_name_buffer' not in st.session_state:
        st.session_state.new_freediver_full_name_buffer = ""

    st.set_page_config(page_title=_("page_title", st.session_state.language), layout="centered", initial_sidebar_state="expanded", page_icon="📒",)

    st.markdown("""
        <style>
            [data-testid="stSidebar"] [data-testid="stForm"] {
                background: white;
                border: 3px solid #DCE6F4;
                border-radius: 10px;
                padding: 20px;
            }

            [data-testid="stTextInput"] input,
            [data-testid="stNumberInput"] input,
            [data-testid="stDateInput"] input,
            [data-testid="stTimeInput"] input,
            [data-testid="stTextArea"] textarea {
                border: 0px solid #FAFAFA;
                border-radius: 0px;
            }

            [data-testid="stExpander"] details {
                border: none !important;
                box-shadow: none !important;
            }
            
        </style>
        """, unsafe_allow_html=True)

    config = get_auth_config()

    if st.session_state['authentication_status']:
        main_app()
    else:
        display_login_form(config, st.session_state.language)


if __name__ == "__main__":
    main()