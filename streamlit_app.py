import streamlit as st
import pandas as pd
import json
from datetime import datetime, date, time
import uuid # Added for unique record IDs
import altair as alt # Added for advanced charting

RECORDS_FILE = "freediving_records.json"
USER_PROFILES_FILE = "user_profiles.json"
TRAINING_LOG_FILE = "training_log.json"
INSTRUCTOR_FEEDBACK_FILE = "instructor_feedback.json"

# --- Privileged User Configuration ---
PRIVILEGED_USERS = ["Philippe K.", "Vincent C.", "Charles D.B.", "Rémy L.", "Gregory D."]
CORRECT_PASSWORD = "M@capnée" # Ensure this is a secure password in a real application

# Instructor certification levels for different functionalities
INSTRUCTOR_CERT_LEVELS_FOR_LOGGING_FEEDBACK_SIDEBAR = ["S4", "I1", "I2", "I3"]
INSTRUCTOR_CERT_LEVELS_FOR_ADMIN_TABS_AND_DROPDOWNS = ["A3", "S4", "I1", "I2", "I3"]

# --- Language Translations (ensure "freediver" and "apnéiste" are used consistently) ---
TRANSLATIONS = {
    "en": {
        "page_title": "Freediving Logbook",
        "app_title": "🌊 Freediving Performance Tracker",
        "user_management_header": "👤 Freediver Management",
        "no_users_yet": "No freedivers yet. Add a new freediver to begin.",
        "enter_freediver_name_sidebar": "Enter New Freediver Name (Format: Firstname L.)",
        "confirm_freediver_button_sidebar": "Show Freediver Data",
        "new_user_success": "New freediver: **{user}**. Profile/performance to be saved to finalize.", 
        "select_user_or_add": "Select Freediver", 
        "add_new_user_option": "✨ Add New Freediver...",
        "existing_user_selected": "Freediver **{user}** confirmed.", 
        "log_performance_header": "✏️ Log New Performance",
        "profile_header_sidebar": "🪪 Freediver Profile",
        "select_user_first_warning": "Confirm or add a freediver first to log performances.",
        "logging_for": "Logging for: **{user}**",
        "link_training_session_label": "Training Session",
        "no_specific_session_option": "Custom Event / No specific session",
        "entry_date_label": "Entry Date",
        "discipline": "Discipline",
        "performance_value": "Performance Value",
        "sta_help": "Format: MM:SS (e.g., 03:45). Milliseconds will be ignored for display.",
        "dyn_depth_help": "Format: Number, optionally followed by 'm' (e.g., 75 or 75m)",
        "save_performance_button": "💾 Save Performance",
        "performance_value_empty_error": "Performance value cannot be empty.",
        "event_name_empty_error": "Event name cannot be empty (if no training session is linked).", 
        "performance_saved_success": "Performance saved for {user}!",
        "process_performance_error": "Failed to process performance value. Please check format.",
        "my_performances_header": "📬 My Performances ({user})",
        "personal_records_tab_label": "📊 My Performances",
        "select_user_to_view_personal_records": "Please confirm a freediver from the sidebar to view their personal records.",
        "no_performances_yet": "No performances logged yet for this freediver. Add some using the sidebar!",
        "personal_bests_subheader": "🌟 Personal Bests",
        "club_bests_subheader": "🏆 Club Best Performances",
        "pb_label": "PB {discipline_short_name}",
        "club_best_label": "Club Best {discipline_short_name}",
        "achieved_at_event_on_date_caption": "By {user} at {event_name} on {event_date}",
        "achieved_on_event_caption": "Achieved at {event_name} on: {event_date}",
        "no_record_yet_caption": "No record yet",
        "performance_evolution_subheader": "📈 Performance Evolution",
        "seconds_unit": "seconds",
        "meters_unit": "meters",
        "history_table_subheader": "📜 History Table (Editable)",
        "full_history_subheader": "📜 Full History",
        "history_event_name_col": "Event Name",
        "history_event_date_col": "Event Date",
        "history_entry_date_col": "Entry Date",
        "history_discipline_col": "Discipline",
        "history_performance_col": "Performance",
        "history_actions_col": "Actions",
        "history_delete_col_editor": "Delete?",
        "no_history_display": "No history to display for this discipline.",
        "no_data_for_graph": "No data to display graph for this discipline.",
        "welcome_message": "👋 Welcome to the Freediving Tracker! Please select or add your first freediver in the sidebar and confirm to get started.",
        "select_user_prompt": "Please select or add a freediver in the sidebar, then confirm, to view and log performances.",
        "language_select_label": "🌐 Language / Langue / Taal",
        "invalid_time_format": "Invalid time format '{time_str}'. Expected MM:SS or MM:SS.ms",
        "invalid_ms_format": "Invalid millisecond format in '{time_str}'.",
        "time_values_out_of_range": "Time values out of range in '{time_str}'.",
        "could_not_parse_time": "Could not parse time string '{time_str}'. Ensure numbers are used correctly.",
        "distance_empty_error": "Distance value cannot be empty.",
        "distance_negative_error": "Distance cannot be negative.",
        "invalid_distance_format": "Invalid distance format '{dist_str}'. Use a number, optionally followed by 'm'.",
        "disciplines": {
            "Static Apnea (STA)": "Static Apnea (STA)",
            "Dynamic Bi-fins (DYN-BF)": "Dynamic Bi-fins (DYN-BF)",
            "Depth (CWT/FIM)": "Depth (CWT/FIM)",
            "Profondeur (VWT/NLT)": "Depth (VWT/NLT)",
            "16x25m Speed Endurance": "16x25m Speed Endurance"
        },
        "club_performances_overview_tab_label": "🏆 Club Performances",
        "select_discipline_for_ranking": "Select discipline for ranking:",
        "podium_header": "🏆 Podium",
        "full_ranking_header": "📋 Full Ranking",
        "rank_col": "Rank",
        "user_col": "Freediver", 
        "best_performance_col": "Best Performance",
        "event_col": "Event",
        "date_achieved_col": "Event Date", 
        "no_ranking_data": "No ranking data available for this discipline yet.",
        "profile_tab_title": "🪪 Freediver Profile",
        "certification_label": "Certification Level:",
        "certification_date_label": "Certification Date:",
        "lifras_id_label": "LIFRAS ID:",
        "anonymize_results_label": "Anonymize my results",
        "anonymize_results_col_editor": "Anonymize?",
        "anonymous_freediver_name": "Anonymous Freediver", 
        "save_profile_button": "💾 Save Profile",
        "profile_saved_success": "Profile saved successfully for {user}!",
        "select_user_to_edit_profile": "Confirm a freediver from the sidebar to view or edit their profile.",
        "no_certification_option": "Not Specified",
        "certification_levels": {
            "A1": "A1", "A2": "A2", "A3": "A3", "S4": "S4",
            "I1": "I1", "I2": "I2", "I3": "I3", "NB": "NB"
        },
        "certification_stats_header": "📊 Certification Level Statistics",
        "certification_level_col": "Certification Level",
        "min_performance_col": "Min Performance",
        "max_performance_col": "Max Performance",
        "avg_performance_col": "Avg Performance",
        "no_stats_data": "No data available for certification statistics in this discipline.",
        "edit_action": "Edit",
        "delete_action": "Delete",
        "edit_performance_header": "✏️ Edit Performance",
        "save_changes_button": "💾 Save Changes",
        "save_history_changes_button": "💾 Save History Changes",
        "cancel_edit_button": "❌ Cancel Edit",
        "confirm_delete_button": "🗑️ Confirm Delete",
        "delete_confirmation_prompt": "Are you sure you want to delete this performance: {event_date} at {event_name} - {performance}?",
        "performance_deleted_success": "Performance deleted successfully.",
        "no_record_found_for_editing": "Error: Could not find the record to edit.",
        "performance_updated_success": "Performance updated successfully.",
        "history_updated_success": "History updated successfully.",
        "critical_error_edit_id_not_found": "Critical error: Record ID '{record_id}' to edit not found in master list. Edit cancelled.",
        "club_performances_tab_title": "📈 Club Performances",
        "no_data_for_club_performance_display": "No performance data available for the club in this discipline.",
        "quarterly_average_label": "Quarterly Average",
        "freedivers_tab_title": "🫂 Freedivers", 
        "edit_freedivers_header": "Edit Freediver Information", 
        "freediver_name_col_editor": "Freediver Name (First L.)", 
        "certification_col_editor": "Certification Level",
        "certification_date_col_editor": "Cert. Date",
        "lifras_id_col_editor": "LIFRAS ID",
        "pb_sta_col_editor": "PB STA",
        "pb_dynbf_col_editor": "PB DYN-BF",
        "pb_depth_col_editor": "PB Depth",
        "pb_vwt_nlt_col_editor": "PB Depth (VWT/NLT)",
        "pb_16x25_col_editor": "PB 16x25m",
        "save_freedivers_changes_button": "💾 Save Freediver Changes", 
        "freedivers_updated_success": "Freediver data updated successfully.", 
        "freediver_name_conflict_error": "Error: Name '{new_name}' is already in use by another freediver. Please choose a unique name.", 
        "original_name_col_editor_hidden": "original_name",
        "freediver_certification_summary_header": "🔢 Freedivers per Certification Level", 
        "count_col": "Count",
        "training_log_tab_title": "📅 Training Log",
        "log_training_header_sidebar": "🏋️ Log New Training Session",
        "training_date_label": "Training Date",
        "training_place_label": "Place",
        "training_description_label": "Description",
        "save_training_button": "💾 Save Training Session",
        "training_session_saved_success": "Training session saved!",
        "training_description_empty_error": "Training description cannot be empty.",
        "training_log_table_header": "📋 Training Sessions (Editable)",
        "save_training_log_changes_button": "💾 Save Training Log Changes",
        "training_log_updated_success": "Training log updated successfully.",
        "performance_log_tab_label": "📜 Performance Log",
        "save_all_performances_button": "💾 Save Performance Log Changes",
        "all_performances_updated_success": "Performance log updated successfully.",
        "feedback_log_tab_label": "💬 Feedback Log",
        "feedbacks_overview_tab_label": "💬 Feedbacks",
        "edit_feedbacks_sub_tab_label": "📝 Edit Feedbacks",
        "log_feedback_header_sidebar": "📝 Log Instructor Feedback",
        "feedback_for_freediver_label": "Feedback for Freediver:", 
        "training_session_label": "Linked Training Session:",
        "instructor_name_label": "Instructor Name:",
        "feedback_text_label": "Feedback:",
        "save_feedback_button": "💾 Save Feedback",
        "feedback_saved_success": "Feedback saved successfully!",
        "feedback_text_empty_error": "Feedback text cannot be empty.",
        "feedback_log_table_header": "📋 Feedback Log (Editable)",
        "save_feedback_log_changes_button": "💾 Save Feedback Log Changes",
        "feedback_log_updated_success": "Feedback log updated successfully.",
        "no_feedback_for_user": "No feedback received yet.",
        "no_feedback_in_log": "No feedback logged in the system yet.",
        "feedback_date_col": "Feedback Date",
        "select_training_prompt": "Select a training session (optional)",
        "select_freediver_prompt": "Select Freediver", 
        "select_instructor_prompt": "Select Instructor",
        "detailed_training_sessions_subheader": "Detailed Training Sessions",
        "training_sessions_sub_tab_label": "🗓️ Training Sessions",
        "edit_training_sessions_sub_tab_label": "✏️ Edit Training Sessions",
        "no_description_available": "No description available.",
        "no_training_sessions_logged": "No training sessions logged yet.",
        "filter_by_freediver_label": "Filter by Freediver:", 
        "filter_by_training_session_label": "Filter by Training Session:",
        "filter_by_instructor_label": "Filter by Instructor:",
        "all_freedivers_option": "All Freedivers", 
        "all_sessions_option": "All Sessions",
        "all_instructors_option": "All Instructors",
        "no_feedbacks_match_filters": "No feedbacks match the current filters.",
        "enter_access_code_prompt": "Enter access code:",
        "unlock_button_label": "Unlock Privileged Access",
        "access_unlocked_success": "Privileged access unlocked!",
        "incorrect_access_code_error": "Incorrect access code."
    },
    "fr": {
        "page_title": "Carnet d'Apnée",
        "app_title": "🌊 Suivi des Performances d'Apnée",
        "user_management_header": "👤 Gestion des Apnéistes",
        "no_users_yet": "Aucun apnéiste pour le moment. Ajoutez-en un via l'onglet Apnéistes.",
        "enter_freediver_name_sidebar": "Entrez le nom du Nouvel Apnéiste (Format: Prénom L.)",
        "confirm_freediver_button_sidebar": "Afficher les Données",
        "new_user_success": "Nouvel apnéiste : **{user}**. Profil/performance à sauvegarder pour finaliser.",
        "select_user_or_add": "Sélectionnez un apnéiste",
        "add_new_user_option": "✨ Ajouter un nouvel apnéiste...",
        "existing_user_selected": "Apnéiste **{user}** confirmé.",
        "log_performance_header": "✏️ Enregistrer une nouvelle performance",
        "profile_header_sidebar": "🪪 Profil Apnéiste",
        "select_user_first_warning": "Confirmez ou ajoutez d'abord un apnéiste pour enregistrer des performances.",
        "logging_for": "Enregistrement pour : **{user}**",
        "link_training_session_label": "Session d'Entraînement",
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
        "select_user_to_view_personal_records": "Veuillez confirmer un apnéiste dans la barre latérale pour voir ses records personnels.",
        "no_performances_yet": "Aucune performance enregistrée pour cet apnéiste. Ajoutez-en via la barre latérale !",
        "personal_bests_subheader": "🌟 Records Personnels",
        "club_bests_subheader": "🏆 Meilleures Performances du Club",
        "pb_label": "RP {discipline_short_name}",
        "club_best_label": "Record Club {discipline_short_name}",
        "achieved_at_event_on_date_caption": "Par {user} à {event_name} le {event_date}",
        "achieved_on_event_caption": "Réalisé à {event_name} le : {event_date}",
        "no_record_yet_caption": "Aucun record pour l'instant",
        "performance_evolution_subheader": "📈 Évolution des Performances",
        "seconds_unit": "secondes",
        "meters_unit": "mètres",
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
        "welcome_message": "👋 Bienvenue sur le Suivi d'Apnée ! Veuillez sélectionner ou ajouter votre premier apnéiste dans la barre latérale et confirmer pour commencer.",
        "select_user_prompt": "Veuillez sélectionner ou ajouter un apnéiste dans la barre latérale, puis confirmer, pour voir et enregistrer les performances.",
        "language_select_label": "🌐 Language / Langue / Taal",
        "invalid_time_format": "Format de temps invalide '{time_str}'. Attendu MM:SS ou MM:SS.ms",
        "invalid_ms_format": "Format des millisecondes invalide dans '{time_str}'.",
        "time_values_out_of_range": "Valeurs de temps hors limites dans '{time_str}'.",
        "could_not_parse_time": "Impossible d'analyser la chaîne de temps '{time_str}'. Assurez-vous que les nombres sont corrects.",
        "distance_empty_error": "La valeur de distance ne peut pas être vide.",
        "distance_negative_error": "La distance ne peut pas être négative.",
        "invalid_distance_format": "Format de distance invalide '{dist_str}'. Utilisez un nombre, optionnellement suivi de 'm'.",
        "disciplines": {
            "Static Apnea (STA)": "Apnée Statique (STA)",
            "Dynamic Bi-fins (DYN-BF)": "Dynamique Bi-palmes (DYN-BF)",
            "Depth (CWT/FIM)": "Profondeur (CWT/FIM)",
            "Profondeur (VWT/NLT)": "Profondeur (VWT/NLT)",
            "16x25m Speed Endurance": "16x25m Vitesse Endurance"
        },
        "club_performances_overview_tab_label": "🏆 Performances du Club",
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
        "select_user_to_edit_profile": "Confirmez un apnéiste dans la barre latérale pour voir ou modifier son profil.",
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
        "no_data_for_club_performance_display": "Aucune donnée de performance disponible pour le club dans cette discipline.",
        "quarterly_average_label": "Moyenne Trimestrielle",
        "freedivers_tab_title": "🫂 Apnéistes", 
        "edit_freedivers_header": "Modifier les Informations des Apnéistes", 
        "freediver_name_col_editor": "Nom Apnéiste (Prénom L.)", 
        "certification_col_editor": "Niveau de Brevet",
        "certification_date_col_editor": "Date Brevet",
        "lifras_id_col_editor": "ID LIFRAS",
        "pb_sta_col_editor": "RP STA",
        "pb_dynbf_col_editor": "RP DYN-BF",
        "pb_depth_col_editor": "RP Profondeur",
        "pb_vwt_nlt_col_editor": "RP Prof. (VWT/NLT)",
        "pb_16x25_col_editor": "RP 16x25m",
        "save_freedivers_changes_button": "💾 Sauvegarder les Apnéistes", 
        "freedivers_updated_success": "Données des apnéistes mises à jour avec succès.", 
        "freediver_name_conflict_error": "Erreur : Le nom '{new_name}' est déjà utilisé par un autre apnéiste. Veuillez choisir un nom unique.", 
        "original_name_col_editor_hidden": "nom_original",
        "freediver_certification_summary_header": "🔢 Apnéistes par Niveau de Brevet", 
        "count_col": "Nombre",
        "training_log_tab_title": "📅 Journal d'Entraînement",
        "log_training_header_sidebar": "🏋️ Enregistrer un Nouvel Entraînement",
        "training_date_label": "Date de l'Entraînement",
        "training_place_label": "Lieu",
        "training_description_label": "Description",
        "save_training_button": "💾 Enregistrer l'Entraînement",
        "training_session_saved_success": "Session d'entraînement enregistrée !",
        "training_description_empty_error": "La description de l'entraînement ne peut pas être vide.",
        "training_log_table_header": "📋 Sessions d'Entraînement (Modifiable)",
        "save_training_log_changes_button": "💾 Sauvegarder le Journal d'Entraînement",
        "training_log_updated_success": "Journal d'entraînement mis à jour avec succès.",
        "performance_log_tab_label": "📜 Journal des Performances",
        "save_all_performances_button": "💾 Sauvegarder les Modifications du Journal",
        "all_performances_updated_success": "Journal des performances mis à jour avec succès.",
        "feedback_log_tab_label": "💬 Journal des Feedbacks", 
        "feedbacks_overview_tab_label": "💬 Feedbacks", 
        "edit_feedbacks_sub_tab_label": "📝 Modifier Feedbacks", 
        "log_feedback_header_sidebar": "📝 Enregistrer Feedback Instructeur",
        "feedback_for_freediver_label": "Feedback pour l'Apnéiste :", 
        "training_session_label": "Session d'Entraînement Liée :",
        "instructor_name_label": "Nom de l'Instructeur :",
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
        "detailed_training_sessions_subheader": "Détail des Sessions d'Entraînement",
        "training_sessions_sub_tab_label": "🗓️ Sessions d'Entraînement", 
        "edit_training_sessions_sub_tab_label": "✏️ Modifier Sessions d'Entraînement", 
        "no_description_available": "Aucune description disponible.",
        "no_training_sessions_logged": "Aucune session d'entraînement enregistrée pour le moment.",
        "filter_by_freediver_label": "Filtrer par Apnéiste :", 
        "filter_by_training_session_label": "Filtrer par Session d'Entraînement :",
        "filter_by_instructor_label": "Filtrer par Instructeur :",
        "all_freedivers_option": "Tous les Apnéistes", 
        "all_sessions_option": "Toutes les Sessions",
        "all_instructors_option": "Tous les Instructeurs",
        "no_feedbacks_match_filters": "Aucun feedback ne correspond aux filtres actuels.",
        "enter_access_code_prompt": "Entrez le code d'accès :",
        "unlock_button_label": "Déverrouiller Accès Privilégié",
        "access_unlocked_success": "Accès privilégié déverrouillé !",
        "incorrect_access_code_error": "Code d'accès incorrect."
    },
    "nl": {
        "page_title": "Vrijduik Logboek",
        "app_title": "🌊 Vrijduik Prestatie Tracker",
        "user_management_header": "👤 Vrijduiker Beheer", 
        "no_users_yet": "Nog geen vrijduikers. Voeg een nieuwe vrijduiker toe om te beginnen.", 
        "enter_freediver_name_sidebar": "Voer Naam Nieuwe Vrijduiker in (Formaat: Voornaam L.)", 
        "confirm_freediver_button_sidebar": "Toon Vrijduiker Gegevens", 
        "new_user_success": "Nieuwe vrijduiker: **{user}**. Profiel/prestatie op te slaan om te finaliseren.", 
        "select_user_or_add": "Selecteer Vrijduiker", 
        "add_new_user_option": "✨ Nieuwe vrijduiker toevoegen...", 
        "existing_user_selected": "Vrijduiker **{user}** bevestigd.", 
        "log_performance_header": "✏️ Log Nieuwe Prestatie",
        "profile_header_sidebar": "🪪 Vrijduiker Profiel", 
        "select_user_first_warning": "Bevestig of voeg eerst een vrijduiker toe om prestaties te loggen.", 
        "logging_for": "Loggen voor: **{user}**",
        "link_training_session_label": "Trainingssessie",
        "no_specific_session_option": "Aangepast evenement / Geen specifieke sessie",
        "entry_date_label": "Invoerdatum",
        "discipline": "Discipline",
        "performance_value": "Prestatiewaarde",
        "sta_help": "Formaat: MM:SS (bijv. 03:45). Milliseconden worden genegeerd voor weergave.",
        "dyn_depth_help": "Formaat: Getal, optioneel gevolgd door 'm' (bijv. 75 of 75m)",
        "save_performance_button": "💾 Prestatie Opslaan",
        "performance_value_empty_error": "Prestatiewaarde mag niet leeg zijn.",
        "event_name_empty_error": "Naam van het evenement mag niet leeg zijn (indien geen trainingssessie gekoppeld).",
        "performance_saved_success": "Prestatie opgeslagen voor {user}!",
        "process_performance_error": "Kon prestatiewaarde niet verwerken. Controleer het formaat.",
        "my_performances_header": "📬 Mijn Prestaties ({user})",
        "personal_records_tab_label": "📊 Mijn Prestaties",
        "select_user_to_view_personal_records": "Bevestig een vrijduiker in de zijbalk om persoonlijke records te bekijken.", 
        "no_performances_yet": "Nog geen prestaties gelogd voor deze vrijduiker. Voeg er enkele toe via de zijbalk!", 
        "personal_bests_subheader": "🌟 Persoonlijke Records",
        "club_bests_subheader": "🏆 Club Beste Prestaties",
        "pb_label": "PR {discipline_short_name}",
        "club_best_label": "Clubrecord {discipline_short_name}",
        "achieved_at_event_on_date_caption": "Door {user} op {event_name} op {event_date}",
        "achieved_on_event_caption": "Behaald op {event_name} op: {event_date}",
        "no_record_yet_caption": "Nog geen record",
        "performance_evolution_subheader": "📈 Prestatie-evolutie",
        "seconds_unit": "seconden",
        "meters_unit": "meter",
        "history_table_subheader": "📜 Geschiedenistabel (Bewerkbaar)",
        "full_history_subheader": "📜 Volledige Geschiedenis",
        "history_event_name_col": "Naam Evenement",
        "history_event_date_col": "Datum Evenement",
        "history_entry_date_col": "Invoerdatum",
        "history_discipline_col": "Discipline",
        "history_performance_col": "Prestatie",
        "history_actions_col": "Acties",
        "history_delete_col_editor": "Verwijderen?",
        "no_history_display": "Geen geschiedenis om weer te geven voor deze discipline.",
        "no_data_for_graph": "Geen gegevens om grafiek weer te geven voor deze discipline.",
        "welcome_message": "👋 Welkom bij de Vrijduik Tracker! Selecteer of voeg uw eerste vrijduiker toe in de zijbalk en bevestig om te beginnen.", 
        "select_user_prompt": "Selecteer of voeg een vrijduiker toe in de zijbalk, en bevestig, om prestaties te bekijken en te loggen.", 
        "language_select_label": "🌐 Language / Langue / Taal",
        "invalid_time_format": "Ongeldig tijdformaat '{time_str}'. Verwacht MM:SS of MM:SS.ms",
        "invalid_ms_format": "Ongeldig millisecondeformaat in '{time_str}'.",
        "time_values_out_of_range": "Tijdswaarden buiten bereik in '{time_str}'.",
        "could_not_parse_time": "Kon tijdreeks '{time_str}' niet parseren. Zorg ervoor dat de nummers correct zijn.",
        "distance_empty_error": "Afstandswaarde mag niet leeg zijn.",
        "distance_negative_error": "Afstand kan niet negatief zijn.",
        "invalid_distance_format": "Ongeldig afstandsformaat '{dist_str}'. Gebruik een getal, optioneel gevolgd door 'm'.",
        "disciplines": {
            "Static Apnea (STA)": "Statische Apneu (STA)",
            "Dynamic Bi-fins (DYN-BF)": "Dynamisch Bi-vinnen (DYN-BF)",
            "Depth (CWT/FIM)": "Diepte (CWT/FIM)",
            "Profondeur (VWT/NLT)": "Diepte (VWT/NLT)",
            "16x25m Speed Endurance": "16x25m Snelheid Uithouding"
        },
        "club_performances_overview_tab_label": "🏆 Clubprestaties",
        "select_discipline_for_ranking": "Selecteer discipline voor klassement:",
        "podium_header": "🏆 Podium",
        "full_ranking_header": "📋 Volledig Klassement",
        "rank_col": "Rang",
        "user_col": "Vrijduiker", 
        "best_performance_col": "Beste Prestatie",
        "event_col": "Evenement",
        "date_achieved_col": "Datum Evenement", 
        "no_ranking_data": "Nog geen klassementgegevens beschikbaar voor deze discipline.",
        "profile_tab_title": "🪪 Vrijduiker Profiel", 
        "certification_label": "Certificeringsniveau:",
        "certification_date_label": "Certificatiedatum:",
        "lifras_id_label": "LIFRAS ID:",
        "anonymize_results_label": "Mijn resultaten anonimiseren",
        "anonymize_results_col_editor": "Anonimiseren?",
        "anonymous_freediver_name": "Anonieme Vrijduiker", 
        "save_profile_button": "💾 Profiel Opslaan",
        "profile_saved_success": "Profiel succesvol opgeslagen voor {user}!",
        "select_user_to_edit_profile": "Bevestig een vrijduiker in de zijbalk om hun profiel te bekijken of te bewerken.", 
        "no_certification_option": "Niet Gespecificeerd",
        "certification_levels": {
            "A1": "A1", "A2": "A2", "A3": "A3", "S4": "S4",
            "I1": "I1", "I2": "I2", "I3": "I3", "NB": "NB"
        },
        "certification_stats_header": "📊 Certificatieniveau Statistieken",
        "certification_level_col": "Certificatieniveau",
        "min_performance_col": "Min Prestatie",
        "max_performance_col": "Max Prestatie",
        "avg_performance_col": "Gem Prestatie",
        "no_stats_data": "Geen gegevens beschikbaar voor certificatiestatistieken in deze discipline.",
        "edit_action": "Bewerken",
        "delete_action": "Verwijderen",
        "edit_performance_header": "✏️ Prestatie Bewerken",
        "save_changes_button": "💾 Wijzigingen Opslaan",
        "save_history_changes_button": "💾 Geschiedenis Opslaan",
        "cancel_edit_button": "❌ Bewerken Annuleren",
        "confirm_delete_button": "🗑️ Verwijderen Bevestigen",
        "delete_confirmation_prompt": "Weet u zeker dat u deze prestatie wilt verwijderen: {event_date} bij {event_name} - {performance}?",
        "performance_deleted_success": "Prestatie succesvol verwijderd.",
        "no_record_found_for_editing": "Fout: Kon de te bewerken record niet vinden.",
        "performance_updated_success": "Prestatie succesvol bijgewerkt.",
        "history_updated_success": "Geschiedenis succesvol bijgewerkt.",
        "critical_error_edit_id_not_found": "Kritieke fout: Record-ID '{record_id}' om te bewerken niet gevonden in hoofdlijst. Bewerken geannuleerd.",
        "club_performances_tab_title": "📈 Clubprestaties",
        "no_data_for_club_performance_display": "Geen prestatiegegevens beschikbaar voor de club in deze discipline.",
        "quarterly_average_label": "Kwartaalgemiddelde",
        "freedivers_tab_title": "🫂 Vrijduikers", 
        "edit_freedivers_header": "Vrijduikerinformatie Bewerken", 
        "freediver_name_col_editor": "Naam Vrijduiker (Voornaam L.)", 
        "certification_col_editor": "Certificeringsniveau",
        "certification_date_col_editor": "Cert. Datum",
        "lifras_id_col_editor": "LIFRAS ID",
        "pb_sta_col_editor": "PR STA",
        "pb_dynbf_col_editor": "PR DYN-BF",
        "pb_depth_col_editor": "PR Diepte",
        "pb_vwt_nlt_col_editor": "PR Diepte (VWT/NLT)",
        "pb_16x25_col_editor": "PR 16x25m",
        "save_freedivers_changes_button": "💾 Vrijduikers Opslaan", 
        "freedivers_updated_success": "Vrijduikergegevens succesvol bijgewerkt.", 
        "freediver_name_conflict_error": "Fout: Naam '{new_name}' is al in gebruik door een andere vrijduiker. Kies een unieke naam.", 
        "original_name_col_editor_hidden": "originele_naam",
        "freediver_certification_summary_header": "🔢 Vrijduikers per Certificatieniveau", 
        "count_col": "Aantal",
        "training_log_tab_title": "📅 Trainingslogboek",
        "log_training_header_sidebar": "🏋️ Nieuwe Trainingssessie Loggen",
        "training_date_label": "Trainingsdatum",
        "training_place_label": "Plaats",
        "training_description_label": "Beschrijving",
        "save_training_button": "💾 Trainingssessie Opslaan",
        "training_session_saved_success": "Trainingssessie opgeslagen!",
        "training_description_empty_error": "Trainingsbeschrijving mag niet leeg zijn.",
        "training_log_table_header": "📋 Trainingssessies (Bewerkbaar)",
        "save_training_log_changes_button": "💾 Trainingslogboek Opslaan",
        "training_log_updated_success": "Trainingslogboek succesvol bijgewerkt.",
        "performance_log_tab_label": "📜 Prestatielogboek",
        "save_all_performances_button": "💾 Prestatielogboekwijzigingen Opslaan",
        "all_performances_updated_success": "Prestatielogboek succesvol bijgewerkt.",
        "feedback_log_tab_label": "💬 Feedbacklogboek",
        "feedbacks_overview_tab_label": "💬 Feedbacks",
        "edit_feedbacks_sub_tab_label": "📝 Feedbacks Bewerken",
        "log_feedback_header_sidebar": "📝 Instructeurfeedback Loggen",
        "feedback_for_freediver_label": "Feedback voor Vrijduiker:", 
        "training_session_label": "Gekoppelde Trainingssessie:",
        "instructor_name_label": "Naam Instructeur:",
        "feedback_text_label": "Feedback:",
        "save_feedback_button": "💾 Feedback Opslaan",
        "feedback_saved_success": "Feedback succesvol opgeslagen!",
        "feedback_text_empty_error": "Feedbacktekst mag niet leeg zijn.",
        "feedback_log_table_header": "📋 Feedbacklogboek (Bewerkbaar)",
        "save_feedback_log_changes_button": "💾 Feedbacklogboekwijzigingen Opslaan",
        "feedback_log_updated_success": "Feedbacklogboek succesvol bijgewerkt.",
        "no_feedback_for_user": "Nog geen feedback ontvangen.",
        "no_feedback_in_log": "Nog geen feedback gelogd in het systeem.",
        "feedback_date_col": "Feedbackdatum",
        "select_training_prompt": "Selecteer een trainingssessie (optioneel)",
        "select_freediver_prompt": "Selecteer Vrijduiker", 
        "select_instructor_prompt": "Selecteer Instructeur",
        "detailed_training_sessions_subheader": "Gedetailleerde Trainingssessies",
        "training_sessions_sub_tab_label": "🗓️ Trainingssessies",
        "edit_training_sessions_sub_tab_label": "✏️ Trainingssessies Bewerken",
        "no_description_available": "Geen beschrijving beschikbaar.",
        "no_training_sessions_logged": "Nog geen trainingssessies gelogd.",
        "filter_by_freediver_label": "Filter op Vrijduiker:", 
        "filter_by_training_session_label": "Filter op Trainingssessie:",
        "filter_by_instructor_label": "Filter op Instructeur:",
        "all_freedivers_option": "Alle Vrijduikers", 
        "all_sessions_option": "Alle Sessies",
        "all_instructors_option": "Alle Instructeurs",
        "no_feedbacks_match_filters": "Geen feedbacks komen overeen met de huidige filters.",
        "enter_access_code_prompt": "Voer toegangscode in:",
        "unlock_button_label": "Ontgrendel Bevoorrechte Toegang",
        "access_unlocked_success": "Bevoorrechte toegang ontgrendeld!",
        "incorrect_access_code_error": "Incorrecte toegangscode."
    }
}

# --- Helper to get translated text ---
def _(key, lang=None, **kwargs):
    if lang is None:
        lang = st.session_state.get('language', 'en')
    
    keys = key.split('.')
    translation_set = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    value = translation_set
    try:
        for k_loop in keys:
            value = value[k_loop]
        if kwargs:
            return value.format(**kwargs)
        return value
    except KeyError:
        translation_set_en = TRANSLATIONS['en']
        value_en = translation_set_en
        try:
            for k_en in keys:
                value_en = value_en[k_en]
            if kwargs:
                return value_en.format(**kwargs)
            return value_en
        except KeyError:
            return key

# --- Helper for anonymization ---
def get_display_name(user_name, user_profiles, lang):
    if user_name and user_name in user_profiles:
        if user_profiles[user_name].get("anonymize_results", False):
            return _("anonymous_freediver_name", lang) 
    return user_name


# --- Data Handling for Performance Records ---
def ensure_performance_fields(records_list):
    updated = False
    today_iso = date.today().isoformat()
    for record in records_list:
        if record.get('id') is None:
            record['id'] = uuid.uuid4().hex
            updated = True
        if 'date' in record and 'event_date' not in record:
            record['event_date'] = record.pop('date')
            updated = True
        if 'event_name' not in record or record['event_name'] == "General Training / Unknown":
            record['event_name'] = "Unspecified Training"
            updated = True
        if 'event_date' not in record:
            record['event_date'] = today_iso
            updated = True
        if 'entry_date' not in record:
            record['entry_date'] = record.get('event_date', today_iso)
            updated = True
        if 'linked_training_session_id' not in record:
            record['linked_training_session_id'] = None
    return updated

def load_records():
    try:
        with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        records = []
    if ensure_performance_fields(records): 
        save_records(records)
    return records

def save_records(records):
    with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=4, ensure_ascii=False)

# --- Data Handling for User Profiles ---
def load_user_profiles():
    try:
        with open(USER_PROFILES_FILE, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        profiles = {}
    return profiles

def save_user_profiles(profiles):
    with open(USER_PROFILES_FILE, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=4, ensure_ascii=False)

# --- Data Handling for Training Logs ---
def ensure_training_log_ids(log_list):
    updated = False
    for entry in log_list:
        if entry.get('id') is None:
            entry['id'] = uuid.uuid4().hex
            updated = True
    return updated

def load_training_log():
    try:
        with open(TRAINING_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
    if ensure_training_log_ids(logs):
        save_training_log(logs)
    return logs

def save_training_log(logs):
    with open(TRAINING_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)

# --- Data Handling for Instructor Feedback ---
def ensure_feedback_ids(feedback_list):
    updated = False
    for entry in feedback_list:
        if entry.get('id') is None:
            entry['id'] = uuid.uuid4().hex
            updated = True
    return updated

def load_instructor_feedback():
    try:
        with open(INSTRUCTOR_FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            feedback_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        feedback_data = []
    if ensure_feedback_ids(feedback_data):
        save_instructor_feedback(feedback_data)
    return feedback_data

def save_instructor_feedback(feedback_data):
    with open(INSTRUCTOR_FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(feedback_data, f, indent=4, ensure_ascii=False)

# --- Performance Parsing and Formatting ---
def is_time_based_discipline(discipline_key):
    return discipline_key in ["Static Apnea (STA)", "16x25m Speed Endurance"]

def parse_static_time_to_seconds(time_str, lang='en'):
    try:
        parts = time_str.split(':')
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
    except ValueError: st.error(_("could_not_parse_time", lang, time_str=time_str)); return None

def format_seconds_to_static_time(total_seconds_float):
    if total_seconds_float is None or pd.isna(total_seconds_float): return "N/A"
    total_seconds_float = float(total_seconds_float); rounded_total_seconds = round(total_seconds_float)
    minutes = int(rounded_total_seconds // 60); seconds = int(rounded_total_seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def parse_distance_to_meters(dist_str, lang='en'):
    try:
        cleaned_dist_str = dist_str.lower().replace('m', '').strip()
        if not cleaned_dist_str: st.error(_("distance_empty_error", lang)); return None
        val = int(cleaned_dist_str)
        if val < 0: st.error(_("distance_negative_error", lang)); return None
        return val
    except ValueError: st.error(_("invalid_distance_format", lang, dist_str=dist_str)); return None

# --- Main App ---
def main():
    # Initialize session state variables
    if 'language' not in st.session_state: st.session_state.language = 'en'
    if 'initiate_clear_training_inputs' not in st.session_state: st.session_state.initiate_clear_training_inputs = False
    if 'initiate_clear_feedback_inputs' not in st.session_state: st.session_state.initiate_clear_feedback_inputs = False
    if 'privileged_user_authenticated' not in st.session_state: st.session_state.privileged_user_authenticated = False
    if 'authenticated_privileged_user' not in st.session_state: st.session_state.authenticated_privileged_user = None
    if 'current_user' not in st.session_state: st.session_state.current_user = None 
    
    if 'new_freediver_name_input_buffer_key' not in st.session_state: 
        st.session_state.new_freediver_name_input_buffer_key = ""
    
    # Buffers for form resets
    if 'log_perf_input_buffer' not in st.session_state: st.session_state.log_perf_input_buffer = ""
    if 'log_perf_session_select_buffer' not in st.session_state: st.session_state.log_perf_session_select_buffer = _("no_specific_session_option", st.session_state.language)
    if 'training_place_buffer' not in st.session_state: st.session_state.training_place_buffer = "Blocry"
    if 'training_desc_buffer' not in st.session_state: st.session_state.training_desc_buffer = ""
    
    # Initialize feedback form buffers carefully to avoid issues if lang changes before first use
    default_lang_for_init = st.session_state.get('language', 'en')
    if 'feedback_for_user_buffer' not in st.session_state: 
        st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", default_lang_for_init)
    if 'feedback_training_session_buffer' not in st.session_state: 
        st.session_state.feedback_training_session_buffer = _("select_training_prompt", default_lang_for_init)
    if 'feedback_text_buffer' not in st.session_state: 
        st.session_state.feedback_text_buffer = ""


    lang = st.session_state.language

    if st.session_state.initiate_clear_training_inputs:
        st.session_state.training_place_buffer = "Blocry"
        st.session_state.training_desc_buffer = ""
        st.session_state.initiate_clear_training_inputs = False
    if st.session_state.initiate_clear_feedback_inputs:
        st.session_state.feedback_text_buffer = ""
        st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", lang)
        st.session_state.feedback_training_session_buffer = _("select_training_prompt", lang)
        st.session_state.initiate_clear_feedback_inputs = False

    st.set_page_config(page_title=_("page_title", lang), layout="wide", initial_sidebar_state="expanded")
    st.title(_("app_title", lang))

    all_records_loaded = load_records()
    user_profiles = load_user_profiles()
    training_log_loaded = load_training_log() 
    instructor_feedback_loaded = load_instructor_feedback()

    discipline_keys = ["Dynamic Bi-fins (DYN-BF)", "Static Apnea (STA)", "Depth (CWT/FIM)", "Profondeur (VWT/NLT)", "16x25m Speed Endurance"]
    translated_disciplines_for_display = [_("disciplines." + key, lang) for key in discipline_keys]

    # --- Sidebar: User Management ---
    all_known_users_list = sorted(list(set(r['user'] for r in all_records_loaded).union(set(user_profiles.keys()))))
    
    with st.sidebar.form(key="freediver_selection_form_sidebar", border=False):
        if not all_known_users_list:
            st.warning(_("no_users_yet", lang))
            st.form_submit_button("...", disabled=True)
        else:
            default_selectbox_index = 0
            if st.session_state.current_user and st.session_state.current_user in all_known_users_list:
                try:
                    default_selectbox_index = all_known_users_list.index(st.session_state.current_user)
                except ValueError:
                    pass # Keep default 0
            
            selectbox_choice_user_form = st.selectbox(
                _("select_user_or_add", lang),
                all_known_users_list,
                index=default_selectbox_index,
                key="user_selectbox_in_freediver_form_key"
            )

            submitted_confirm_freediver = st.form_submit_button(_("confirm_freediver_button_sidebar", lang))

            if submitted_confirm_freediver:
                user_to_be_confirmed = selectbox_choice_user_form
                
                if user_to_be_confirmed:
                    if st.session_state.current_user != user_to_be_confirmed:
                        st.session_state.privileged_user_authenticated = False
                        st.session_state.authenticated_privileged_user = None
                        if "password_field_for_unlock_form_key" in st.session_state:
                            st.session_state.password_field_for_unlock_form_key = ""
                    
                    st.session_state.current_user = user_to_be_confirmed
                    st.info(_("existing_user_selected", lang, user=user_to_be_confirmed))
                    st.rerun()

    current_user = st.session_state.current_user 

    if current_user and current_user in PRIVILEGED_USERS:
        if not st.session_state.get('privileged_user_authenticated', False) or \
           st.session_state.get('authenticated_privileged_user') != current_user:
            
            if st.session_state.get('authenticated_privileged_user') != current_user:
                st.session_state.privileged_user_authenticated = False
                st.session_state.authenticated_privileged_user = None
                if "password_field_for_unlock_form_key" in st.session_state: 
                    st.session_state.password_field_for_unlock_form_key = ""


            with st.sidebar.form(key="unlock_privileges_form_sidebar_key"): 
                st.session_state.password_field_for_unlock_form_key = st.text_input(
                    _("enter_access_code_prompt", lang), 
                    type="password"
                )
                submitted_unlock_form = st.form_submit_button(_("unlock_button_label", lang))

                if submitted_unlock_form:
                    if st.session_state.password_field_for_unlock_form_key == CORRECT_PASSWORD: 
                        st.session_state.privileged_user_authenticated = True
                        st.session_state.authenticated_privileged_user = current_user
                        st.success(_("access_unlocked_success", lang))
                        st.rerun() 
                    else:
                        st.error(_("incorrect_access_code_error", lang))
                        st.session_state.privileged_user_authenticated = False
                        st.session_state.authenticated_privileged_user = None

    elif st.session_state.get('privileged_user_authenticated', False): 
        st.session_state.privileged_user_authenticated = False
        st.session_state.authenticated_privileged_user = None
        if "password_field_for_unlock_form_key" in st.session_state:
             st.session_state.password_field_for_unlock_form_key = ""


    is_admin_view_authorized = False
    if current_user in PRIVILEGED_USERS and \
       st.session_state.get('authenticated_privileged_user') == current_user and \
       st.session_state.get('privileged_user_authenticated', False):
        is_admin_view_authorized = True
    
    is_sidebar_instructor_section_visible = False
    if is_admin_view_authorized and current_user in user_profiles:
        user_cert_sidebar = user_profiles[current_user].get("certification")
        if user_cert_sidebar in INSTRUCTOR_CERT_LEVELS_FOR_LOGGING_FEEDBACK_SIDEBAR:
            is_sidebar_instructor_section_visible = True
            
    # --- Sidebar: Profile Section (Moved and put in an expander) ---
    if current_user: 
        with st.sidebar.expander(_("profile_header_sidebar", lang)):
            with st.form(key="profile_form_sidebar_main", border=False): 
                
                user_profile_data_sidebar = user_profiles.get(current_user, {})
                
                current_certification_sidebar = user_profile_data_sidebar.get("certification", _("no_certification_option", lang))
                cert_level_keys_from_dict_sidebar = list(TRANSLATIONS[lang]["certification_levels"].keys())
                actual_selectbox_options_sidebar = [_("no_certification_option", lang)] + cert_level_keys_from_dict_sidebar
                try: current_cert_index_sidebar = actual_selectbox_options_sidebar.index(current_certification_sidebar)
                except ValueError: current_cert_index_sidebar = 0
                
                new_certification_sidebar_form = st.selectbox(
                    _("certification_label", lang), options=actual_selectbox_options_sidebar, 
                    index=current_cert_index_sidebar, key="certification_select_profile_form_sb" 
                )
                
                current_cert_date_str_sidebar = user_profile_data_sidebar.get("certification_date")
                current_cert_date_obj_sidebar = None
                if current_cert_date_str_sidebar:
                    try: current_cert_date_obj_sidebar = date.fromisoformat(current_cert_date_str_sidebar)
                    except ValueError: current_cert_date_obj_sidebar = None
                
                new_cert_date_sidebar_form = st.date_input(
                    _("certification_date_label", lang), value=current_cert_date_obj_sidebar, key="cert_date_profile_form_sb" 
                )
                
                current_lifras_id_sidebar = user_profile_data_sidebar.get("lifras_id", "")
                new_lifras_id_sidebar_form = st.text_input(
                    _("lifras_id_label", lang), value=current_lifras_id_sidebar, key="lifras_id_profile_form_sb" 
                )
                
                current_anonymize_sidebar = user_profile_data_sidebar.get("anonymize_results", False)
                new_anonymize_sidebar_form = st.checkbox(
                    _("anonymize_results_label", lang), value=current_anonymize_sidebar, key="anonymize_profile_form_sb" 
                )
                
                submitted_save_profile = st.form_submit_button(_("save_profile_button", lang))

                if submitted_save_profile:
                    user_profiles.setdefault(current_user, {}) 
                    user_profiles[current_user]["certification"] = st.session_state.certification_select_profile_form_sb
                    cert_date_val = st.session_state.cert_date_profile_form_sb
                    user_profiles[current_user]["certification_date"] = cert_date_val.isoformat() if cert_date_val else None
                    user_profiles[current_user]["lifras_id"] = st.session_state.lifras_id_profile_form_sb.strip()
                    user_profiles[current_user]["anonymize_results"] = st.session_state.anonymize_profile_form_sb
                    save_user_profiles(user_profiles)
                    st.success(_("profile_saved_success", lang, user=current_user))
                    st.rerun()

    # --- Sidebar: Log New Performance ---
    st.sidebar.header(_("log_performance_header", lang))
    if not current_user:
        st.sidebar.warning(_("select_user_first_warning", lang))
    else:
        with st.sidebar.form(key="log_performance_form_sidebar_main"): 
            st.write(_("logging_for", lang, user=current_user))
            
            training_session_options_for_select_perf = {_("no_specific_session_option", lang): "none"} 
            for ts in sorted(training_log_loaded, key=lambda x: x.get('date', '1900-01-01'), reverse=True):
                display_name = f"{ts.get('date')} - {ts.get('place', 'N/A')}" 
                training_session_options_for_select_perf[display_name] = ts.get('id')
            
            select_box_display_options_perf = list(training_session_options_for_select_perf.keys())
            
            default_perf_session_idx = 0
            try:
                default_perf_session_idx = select_box_display_options_perf.index(st.session_state.log_perf_session_select_buffer)
            except (ValueError, KeyError): 
                st.session_state.log_perf_session_select_buffer = _("no_specific_session_option", lang)
                default_perf_session_idx = 0

            selected_training_session_display_name_perf = st.selectbox(
                _("link_training_session_label", lang),
                options=select_box_display_options_perf,
                index=default_perf_session_idx, 
                key="log_perf_session_select_widget_key" 
            )
            
            selected_translated_discipline = st.selectbox(
                _("discipline", lang), translated_disciplines_for_display, key="log_discipline_perf_form_widget_key" 
            )
            
            log_discipline_original_key_perf_form = None 
            for key_iter in discipline_keys:
                if _("disciplines." + key_iter, lang) == selected_translated_discipline:
                    log_discipline_original_key_perf_form = key_iter
                    break

            performance_help_text_perf_form = ""
            if is_time_based_discipline(log_discipline_original_key_perf_form):
                performance_help_text_perf_form = _("sta_help", lang)
            elif log_discipline_original_key_perf_form in ["Dynamic Bi-fins (DYN-BF)", "Depth (CWT/FIM)", "Profondeur (VWT/NLT)"]:
                performance_help_text_perf_form = _("dyn_depth_help", lang)

            log_performance_str_form = st.text_input(
                _("performance_value", lang), 
                value=st.session_state.log_perf_input_buffer, 
                help=performance_help_text_perf_form, 
                key="log_perf_input_form_widget_key"
            ).strip() 

            submitted_save_perf = st.form_submit_button(_("save_performance_button", lang))

            if submitted_save_perf: 
                actual_event_name = "Performance" 
                actual_event_date_iso = date.today().isoformat() 
                actual_linked_training_id = None
                
                sel_ts_disp_name_from_form = st.session_state.log_perf_session_select_widget_key
                sel_ts_id_from_form = training_session_options_for_select_perf.get(sel_ts_disp_name_from_form)

                if sel_ts_id_from_form and sel_ts_id_from_form != "none":
                    linked_session = next((s for s in training_log_loaded if s.get('id') == sel_ts_id_from_form), None)
                    if linked_session:
                        actual_event_date_iso = linked_session.get('date', date.today().isoformat())
                        actual_event_name = f"{linked_session.get('place','Session')} - {linked_session.get('description','Entraînement')}"[:100] 
                        actual_linked_training_id = sel_ts_id_from_form
                
                current_log_perf_str = st.session_state.log_perf_input_form_widget_key
                current_log_disc_key = None
                sel_trans_disc_from_form = st.session_state.log_discipline_perf_form_widget_key
                for key_iter_form in discipline_keys:
                    if _("disciplines." + key_iter_form, lang) == sel_trans_disc_from_form:
                        current_log_disc_key = key_iter_form
                        break
                
                if not current_log_perf_str: 
                    st.error(_("performance_value_empty_error", lang))
                elif not current_log_disc_key: 
                    st.error("Internal error: Discipline key not found during save.")
                else:
                    parsed_value_for_storage = None
                    if is_time_based_discipline(current_log_disc_key):
                        parsed_value_for_storage = parse_static_time_to_seconds(current_log_perf_str, lang)
                    else:
                        parsed_value_for_storage = parse_distance_to_meters(current_log_perf_str, lang)
                    
                    if parsed_value_for_storage is not None:
                        new_record = {
                            "id": uuid.uuid4().hex, "user": current_user,
                            "event_name": actual_event_name, "event_date": actual_event_date_iso,
                            "entry_date": date.today().isoformat(), "discipline": current_log_disc_key,
                            "original_performance_str": current_log_perf_str, "parsed_value": parsed_value_for_storage,
                            "linked_training_session_id": actual_linked_training_id
                        }
                        all_records_loaded.append(new_record)
                        save_records(all_records_loaded)
                        if current_user not in user_profiles: 
                            user_profiles[current_user] = {"certification": _("no_certification_option", lang), "certification_date": None, "lifras_id": "", "anonymize_results": False}
                            save_user_profiles(user_profiles)
                        st.success(_("performance_saved_success", lang, user=current_user))
                        st.session_state.log_perf_input_buffer = "" 
                        st.session_state.log_perf_session_select_buffer = _("no_specific_session_option", lang) 
                        st.rerun()
    
    # --- Sidebar: Log New Training Session ---
    if is_sidebar_instructor_section_visible:
        st.sidebar.header(_("log_training_header_sidebar", lang))
        with st.sidebar.form(key="log_training_form_sidebar"): 
            training_date_log_val_form = st.date_input(_("training_date_label", lang), date.today(), key="training_date_form_key")
            training_place_form = st.text_input(_("training_place_label", lang), value=st.session_state.training_place_buffer, key="training_place_form_key")
            training_description_form = st.text_area(_("training_description_label", lang), value=st.session_state.training_desc_buffer, key="training_desc_form_key")
            
            submitted_save_training = st.form_submit_button(_("save_training_button", lang))

            if submitted_save_training:
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
                    st.session_state.training_place_buffer = "Blocry" 
                    st.session_state.training_desc_buffer = ""
                    st.rerun()
    
    # --- Sidebar: Log Instructor Feedback ---
    if is_sidebar_instructor_section_visible:
        st.sidebar.header(_("log_feedback_header_sidebar", lang))
        with st.sidebar.form(key="log_feedback_form_sidebar"): 
            if not all_known_users_list: st.warning("Please add freedivers before logging feedback.") 
            else:
                freediver_options_for_feedback = [_("select_freediver_prompt", lang)] + all_known_users_list # Allow selecting self
                
                default_fb_user_idx = 0
                try:
                    default_fb_user_idx = freediver_options_for_feedback.index(st.session_state.feedback_for_user_buffer)
                except (ValueError, KeyError):
                    st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", lang)

                feedback_for_user_sb_key_form = "feedback_for_user_selectbox_key_in_form" # New key
                feedback_for_user_form = st.selectbox(
                    _("feedback_for_freediver_label", lang), 
                    options=freediver_options_for_feedback, 
                    index=default_fb_user_idx,
                    key=feedback_for_user_sb_key_form
                )
                
                training_session_options_fb_form = {log['id']: f"{log['date']} - {log['place']}" for log in sorted(training_log_loaded, key=lambda x: x['date'], reverse=True)}
                training_session_options_display_fb_form = [_("select_training_prompt", lang)] + list(training_session_options_fb_form.values())
                
                default_fb_ts_idx = 0
                try:
                    default_fb_ts_idx = training_session_options_display_fb_form.index(st.session_state.feedback_training_session_buffer)
                except (ValueError, KeyError):
                    st.session_state.feedback_training_session_buffer = _("select_training_prompt", lang)

                feedback_training_session_sb_key_form = "feedback_training_session_selectbox_key_in_form" # New key
                selected_training_display_fb_form = st.selectbox(
                    _("training_session_label", lang), 
                    options=training_session_options_display_fb_form, 
                    index=default_fb_ts_idx,
                    key=feedback_training_session_sb_key_form
                )
                
                st.write(f"{_('instructor_name_label', lang)} {current_user}") 
                
                feedback_text_area_key_form = "feedback_text_area_key_in_form" # New key
                feedback_text_form = st.text_area(
                    _("feedback_text_label", lang), 
                    value=st.session_state.feedback_text_buffer, 
                    key=feedback_text_area_key_form 
                )

                submitted_save_feedback = st.form_submit_button(_("save_feedback_button", lang))

                if submitted_save_feedback:
                    sel_fb_for_user = st.session_state[feedback_for_user_sb_key_form]
                    sel_fb_training_disp = st.session_state[feedback_training_session_sb_key_form]
                    sel_fb_text = st.session_state[feedback_text_area_key_form].strip() 
                    
                    sel_fb_training_id = None
                    if sel_fb_training_disp != _("select_training_prompt", lang):
                        for log_id, display_str in training_session_options_fb_form.items():
                            if display_str == sel_fb_training_disp: sel_fb_training_id = log_id; break
                    
                    if sel_fb_for_user == _("select_freediver_prompt", lang): st.error("Please select a freediver for the feedback.") 
                    elif not current_user: st.error("Instructor not identified.") 
                    elif not sel_fb_text: st.error(_("feedback_text_empty_error", lang))
                    else:
                        new_feedback = {"id": uuid.uuid4().hex, "feedback_date": date.today().isoformat(), "diver_name": sel_fb_for_user, "training_session_id": sel_fb_training_id, "instructor_name": current_user, "feedback_text": sel_fb_text}
                        instructor_feedback_loaded.append(new_feedback)
                        save_instructor_feedback(instructor_feedback_loaded)
                        st.success(_("feedback_saved_success", lang))
                        st.session_state.feedback_text_buffer = "" 
                        st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", lang)
                        st.session_state.feedback_training_session_buffer = _("select_training_prompt", lang)
                        st.rerun()
                        
    # --- Sidebar: Language Selector (Moved to bottom) ---
    language_options = {"English": "en", "Français": "fr", "Nederlands": "nl"}
    current_lang_display_name = [k_disp for k_disp, v_code in language_options.items() if v_code == lang][0]
    
    # Add a separator for visual distinction
    st.sidebar.markdown("") 
    st.sidebar.markdown("") 
    st.sidebar.markdown("") 

    selected_lang_display_name = st.sidebar.selectbox(
        _("language_select_label", lang), options=list(language_options.keys()),
        index=list(language_options.keys()).index(current_lang_display_name),
        key="language_selector_widget"
    )
    new_lang_code = language_options[selected_lang_display_name]
    if st.session_state.language != new_lang_code:
        st.session_state.language = new_lang_code; st.rerun()
    lang = st.session_state.language

    # --- Main Display Area ---
    tab_label_personal = _("personal_records_tab_label", lang)
    tab_label_main_feedback_log = _("feedback_log_tab_label", lang)
    tab_label_club_performances = _("club_performances_overview_tab_label", lang)
    tab_label_freedivers = _("freedivers_tab_title", lang) 
    tab_label_main_training_log = _("training_log_tab_title", lang)
    tab_label_performance_log = _("performance_log_tab_label", lang)

    if not all_records_loaded and not all_known_users_list and not current_user and not training_log_loaded and not instructor_feedback_loaded:
        st.info(_("welcome_message", lang))
    else:
        tabs_to_display_names_main = [tab_label_personal]
        if is_admin_view_authorized:
            tabs_to_display_names_main.append(tab_label_club_performances)
            tabs_to_display_names_main.append(tab_label_freedivers) 
            tabs_to_display_names_main.append(tab_label_main_training_log)
            tabs_to_display_names_main.append(tab_label_performance_log)
            tabs_to_display_names_main.append(tab_label_main_feedback_log) 
        else:
            tabs_to_display_names_main.append(tab_label_club_performances)
        
        tab_objects_main = st.tabs(tabs_to_display_names_main)
        tab_personal = tab_objects_main[0]
        current_tab_idx = 1
        main_feedback_log_tab_obj, tab_club_performances_view, tab_freedivers, main_training_log_tab_obj, tab_performance_log = None, None, None, None, None 

        if is_admin_view_authorized:
            tab_club_performances_view = tab_objects_main[current_tab_idx]; current_tab_idx += 1
            tab_freedivers = tab_objects_main[current_tab_idx]; current_tab_idx +=1 
            main_training_log_tab_obj = tab_objects_main[current_tab_idx]; current_tab_idx += 1
            tab_performance_log = tab_objects_main[current_tab_idx]; current_tab_idx += 1
            main_feedback_log_tab_obj = tab_objects_main[current_tab_idx] 
        else:
            if len(tab_objects_main) > 1:
                      tab_club_performances_view = tab_objects_main[current_tab_idx]

        with tab_personal:
            if current_user:
                user_records_for_tab = [r for r in all_records_loaded if r['user'] == current_user]
                if not user_records_for_tab:
                    st.info(_("no_performances_yet", lang))
                else:
                    with st.container(border=True):
                        st.subheader(_("personal_bests_subheader", lang))
                        pbs_tab = {}
                        for disc_key_pb_tab in discipline_keys:
                            disc_records_pb_tab = [r_pb_tab for r_pb_tab in user_records_for_tab if r_pb_tab['discipline'] == disc_key_pb_tab and r_pb_tab.get('parsed_value') is not None]
                            if not disc_records_pb_tab:
                                pbs_tab[disc_key_pb_tab] = ("N/A", None, None) 
                                continue
                            if disc_key_pb_tab == "16x25m Speed Endurance":
                                best_record_pb_tab = min(disc_records_pb_tab, key=lambda x_pb_tab: x_pb_tab['parsed_value'])
                            else:
                                best_record_pb_tab = max(disc_records_pb_tab, key=lambda x_pb_tab: x_pb_tab['parsed_value'])
                            if is_time_based_discipline(disc_key_pb_tab):
                                pb_value_formatted_tab = format_seconds_to_static_time(best_record_pb_tab['parsed_value'])
                            else:
                                pb_value_formatted_tab = f"{best_record_pb_tab['parsed_value']}m"
                            pbs_tab[disc_key_pb_tab] = (pb_value_formatted_tab, best_record_pb_tab.get('event_name', "N/A"), best_record_pb_tab.get('event_date', "N/A"))

                        cols_pb_tab = st.columns(len(discipline_keys))
                        for i_pb_col_tab, disc_key_pb_col_tab in enumerate(discipline_keys):
                            val_tab, event_name_tab, event_date_tab = pbs_tab.get(disc_key_pb_col_tab, ("N/A", None, None))
                            with cols_pb_tab[i_pb_col_tab]:
                                translated_full_discipline_name_tab = _("disciplines." + disc_key_pb_col_tab, lang)
                                short_disc_name_tab = translated_full_discipline_name_tab.split('(')[0].strip() or translated_full_discipline_name_tab
                                st.metric(label=_("pb_label", lang, discipline_short_name=short_disc_name_tab), value=val_tab)
                                if event_date_tab and event_date_tab != "N/A": 
                                    st.caption(_("achieved_on_event_caption", lang, event_name=event_name_tab, event_date=event_date_tab))
                                elif val_tab == "N/A": 
                                    st.caption(_("no_record_yet_caption", lang))
                        
                    st.markdown("")
                        
                    sub_tab_titles_user = [_("disciplines." + key, lang) for key in discipline_keys]
                    sub_tabs_user = st.tabs(sub_tab_titles_user)

                    for i_sub_tab_user, disc_key_sub_tab_user in enumerate(discipline_keys):
                        with sub_tabs_user[i_sub_tab_user]:
                            sub_tab_specific_records_user_for_graph = [
                                r_sub_tab_u for r_sub_tab_u in user_records_for_tab
                                if r_sub_tab_u['discipline'] == disc_key_sub_tab_user and r_sub_tab_u.get('parsed_value') is not None and r_sub_tab_u.get('event_date')
                            ]
                            st.markdown(f"#### {_('performance_evolution_subheader', lang)}")
                            if sub_tab_specific_records_user_for_graph:
                                chart_data_list_sub_tab_user = []
                                for r_chart_sub_tab_u in sorted(sub_tab_specific_records_user_for_graph, key=lambda x_chart_u: x_chart_u.get('event_date', '1900-01-01')): 
                                    chart_data_list_sub_tab_user.append({
                                        "Event Date": pd.to_datetime(r_chart_sub_tab_u['event_date']), 
                                        "PerformanceValue": r_chart_sub_tab_u['parsed_value'],
                                        "Event Name": r_chart_sub_tab_u.get('event_name', 'N/A')
                                    })
                                if chart_data_list_sub_tab_user:
                                    chart_df_sub_tab_user = pd.DataFrame(chart_data_list_sub_tab_user)
                                    y_axis_title = _("performance_value", lang) + (f" ({_('seconds_unit', lang)})" if is_time_based_discipline(disc_key_sub_tab_user) else f" ({_('meters_unit', lang)})")
                                    chart_altair = alt.Chart(chart_df_sub_tab_user).mark_line(point=True).encode(
                                        x=alt.X('Event Date:T', title=_("history_event_date_col", lang)), 
                                        y=alt.Y('PerformanceValue:Q', title=y_axis_title),
                                        tooltip=['Event Date:T', 'PerformanceValue:Q', 'Event Name:N']
                                    ).interactive()
                                    st.altair_chart(chart_altair, use_container_width=True)
                                else: st.caption(_("no_data_for_graph", lang))
                            else: st.caption(_("no_data_for_graph", lang))
                            
                            st.markdown(f"#### {_('history_table_subheader', lang)}")
                            history_for_editor_raw = [r for r in user_records_for_tab if r['discipline'] == disc_key_sub_tab_user]
                            if not history_for_editor_raw:
                                st.caption(_("no_history_display", lang))
                            else:
                                history_for_editor_display = []
                                for rec in sorted(history_for_editor_raw, key=lambda x: x.get('event_date', '1900-01-01'), reverse=True):
                                    history_for_editor_display.append({
                                        "id": rec.get("id"),
                                        _("history_event_name_col", lang): rec.get("event_name", "N/A"),
                                        _("history_event_date_col", lang): rec.get("event_date"),
                                        _("history_entry_date_col", lang): rec.get("entry_date"),
                                        _("history_performance_col", lang): rec.get("original_performance_str", ""),
                                        _("history_delete_col_editor", lang): False
                                    })
                                history_df_for_editor = pd.DataFrame(history_for_editor_display)
                                
                                if not history_df_for_editor.empty:
                                    col_event_date_name = _("history_event_date_col", lang)
                                    col_entry_date_name = _("history_entry_date_col", lang)
                                    history_df_for_editor[col_event_date_name] = pd.to_datetime(history_df_for_editor[col_event_date_name], errors='coerce').dt.date
                                    history_df_for_editor[col_entry_date_name] = pd.to_datetime(history_df_for_editor[col_entry_date_name], errors='coerce').dt.date
                                
                                data_editor_key = f"data_editor_{current_user}_{disc_key_sub_tab_user}"
                                edited_df = st.data_editor(
                                    history_df_for_editor,
                                    column_config={
                                        "id": None,
                                        _("history_event_name_col", lang): st.column_config.TextColumn(label=_("history_event_name_col", lang), required=True),
                                        _("history_event_date_col", lang): st.column_config.DateColumn(label=_("history_event_date_col", lang), format="YYYY-MM-DD", required=True),
                                        _("history_entry_date_col", lang): st.column_config.DateColumn(label=_("history_entry_date_col", lang), format="YYYY-MM-DD", disabled=True),
                                        _("history_performance_col", lang): st.column_config.TextColumn(label=_("history_performance_col", lang), required=True),
                                        _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(label=_("history_delete_col_editor", lang), default=False)
                                    },
                                    hide_index=True, key=data_editor_key, num_rows="dynamic"
                                )

                                if st.button(_("save_history_changes_button", lang), key=f"save_hist_{disc_key_sub_tab_user}"):
                                    changes_made = False
                                    temp_all_records_loaded = [r.copy() for r in all_records_loaded]
                                    for index, edited_row_series in edited_df.iterrows():
                                        edited_row = edited_row_series.to_dict()
                                        record_id = edited_row.get("id")
                                        if record_id is None: continue
                                        
                                        original_record_index = next((i for i, r_loop in enumerate(temp_all_records_loaded) if r_loop.get('id') == record_id), -1)
                                        if original_record_index == -1: continue
                                        original_record = temp_all_records_loaded[original_record_index]

                                        if edited_row[_("history_delete_col_editor", lang)]:
                                            del temp_all_records_loaded[original_record_index]
                                            changes_made = True
                                            continue

                                        edited_event_name = edited_row[_("history_event_name_col", lang)].strip()
                                        edited_event_date_obj = edited_row[_("history_event_date_col", lang)]
                                        edited_event_date_str = edited_event_date_obj.isoformat() if isinstance(edited_event_date_obj, date) else str(edited_event_date_obj)
                                        edited_perf_str = str(edited_row[_("history_performance_col", lang)]).strip()
                                        
                                        if not edited_event_name:
                                            st.error(f"Event name cannot be empty for record ID {record_id}. Changes not saved for this row.")
                                            continue

                                        if (original_record.get('event_name') != edited_event_name or
                                            original_record.get('event_date') != edited_event_date_str or
                                            original_record.get('original_performance_str') != edited_perf_str):
                                            
                                            parsed_edited_value = None
                                            current_record_discipline = original_record['discipline']
                                            if is_time_based_discipline(current_record_discipline):
                                                parsed_edited_value = parse_static_time_to_seconds(edited_perf_str, lang)
                                            else:
                                                parsed_edited_value = parse_distance_to_meters(edited_perf_str, lang)
                                            
                                            if parsed_edited_value is None:
                                                st.error(f"Invalid performance format for '{edited_perf_str}' (ID: {record_id}). Changes not saved for this row.")
                                                continue
                                            
                                            temp_all_records_loaded[original_record_index]['event_name'] = edited_event_name
                                            temp_all_records_loaded[original_record_index]['event_date'] = edited_event_date_str
                                            temp_all_records_loaded[original_record_index]['original_performance_str'] = edited_perf_str
                                            temp_all_records_loaded[original_record_index]['parsed_value'] = parsed_edited_value
                                            changes_made = True
                                    
                                    if changes_made:
                                        all_records_loaded[:] = temp_all_records_loaded
                                        save_records(all_records_loaded)
                                        st.success(_("history_updated_success", lang))
                                        st.rerun()
                                    else:
                                        st.info("No changes detected in the history.")
            else:
                st.info(_("select_user_to_view_personal_records", lang))
        
        if is_admin_view_authorized and main_feedback_log_tab_obj: 
            with main_feedback_log_tab_obj:
                sub_tab_fb_overview_label = _("feedbacks_overview_tab_label", lang)
                sub_tab_fb_edit_label = _("edit_feedbacks_sub_tab_label", lang)
                fb_sub_tab1, fb_sub_tab2 = st.tabs([sub_tab_fb_overview_label, sub_tab_fb_edit_label])

                with fb_sub_tab1:
                    st.subheader(_("feedbacks_overview_tab_label", lang))
                    col1_fb_overview, col2_fb_overview, col3_fb_overview = st.columns(3)
                    with col1_fb_overview:
                        freediver_options_filter = [_("all_freedivers_option", lang)] + all_known_users_list 
                        selected_freediver_filter = st.selectbox(_("filter_by_freediver_label", lang), freediver_options_filter, key="fb_overview_freediver_filter_sub") 
                    with col2_fb_overview:
                        training_options_editor_map_feedback_overview = {log['id']: f"{log['date']} - {log['place']}" for log in sorted(training_log_loaded, key=lambda x: x['date'], reverse=True)}
                        training_options_editor_display_with_none_feedback_overview = [_("all_sessions_option", lang)] + list(training_options_editor_map_feedback_overview.values())
                        selected_training_display_filter = st.selectbox(_("filter_by_training_session_label", lang), training_options_editor_display_with_none_feedback_overview, key="fb_overview_session_filter_sub")
                    with col3_fb_overview:
                        instructor_list_for_filter = sorted(list(set(fb['instructor_name'] for fb in instructor_feedback_loaded if fb.get('instructor_name'))))
                        instructor_options_filter = [_("all_instructors_option", lang)] + instructor_list_for_filter
                        selected_instructor_filter = st.selectbox(_("filter_by_instructor_label", lang), instructor_options_filter, key="fb_overview_instructor_filter_sub")

                    selected_training_id_filter = None
                    if selected_training_display_filter != _("all_sessions_option", lang):
                        for log_id, display_str in training_options_editor_map_feedback_overview.items():
                            if display_str == selected_training_display_filter: selected_training_id_filter = log_id; break
                    
                    filtered_feedbacks = instructor_feedback_loaded
                    if selected_freediver_filter != _("all_freedivers_option", lang): 
                        filtered_feedbacks = [fb for fb in filtered_feedbacks if fb.get("diver_name") == selected_freediver_filter] 
                    if selected_training_id_filter:
                        filtered_feedbacks = [fb for fb in filtered_feedbacks if fb.get("training_session_id") == selected_training_id_filter]
                    if selected_instructor_filter != _("all_instructors_option", lang):
                        filtered_feedbacks = [fb for fb in filtered_feedbacks if fb.get("instructor_name") == selected_instructor_filter]

                    if not filtered_feedbacks: st.info(_("no_feedbacks_match_filters", lang))
                    else:
                        for fb_entry in sorted(filtered_feedbacks, key=lambda x: x['feedback_date'], reverse=True):
                            with st.container(border=True):
                                training_session_info_display = "N/A"
                                if fb_entry.get("training_session_id"):
                                    linked_training_fb = next((ts for ts in training_log_loaded if ts.get("id") == fb_entry["training_session_id"]), None)
                                    if linked_training_fb: training_session_info_display = f"{linked_training_fb['date']} - {linked_training_fb['place']}"
                                header_line = f"**{fb_entry['diver_name']}** par **{fb_entry['instructor_name']}** le {fb_entry['feedback_date']}" 
                                if training_session_info_display != "N/A": header_line += f" | Session: {training_session_info_display}"
                                st.markdown(header_line)
                                st.markdown(fb_entry['feedback_text'])

                with fb_sub_tab2:
                    st.subheader(_("feedback_log_table_header", lang))
                    if not instructor_feedback_loaded: st.info(_("no_feedback_in_log", lang))
                    else:
                        feedback_log_display_list = []
                        for fb_item in sorted(instructor_feedback_loaded, key=lambda x: x['feedback_date'], reverse=True):
                            training_info = _("select_training_prompt", lang)
                            if fb_item.get("training_session_id"):
                                linked_training = next((ts for ts in training_log_loaded if ts.get("id") == fb_item["training_session_id"]), None)
                                if linked_training: training_info = f"{linked_training['date']} - {linked_training['place']}"
                            feedback_log_display_list.append({
                                "id": fb_item.get("id"), _("feedback_date_col", lang): fb_item.get("feedback_date"),
                                _("feedback_for_freediver_label", lang): fb_item.get("diver_name"), _("instructor_name_label", lang): fb_item.get("instructor_name"), 
                                _("training_session_label", lang): training_info, "training_session_id_hidden": fb_item.get("training_session_id"),
                                _("feedback_text_label", lang): fb_item.get("feedback_text"), _("history_delete_col_editor", lang): False
                            })
                        feedback_log_df = pd.DataFrame(feedback_log_display_list)
                        if not feedback_log_df.empty:
                            feedback_date_col_name = _("feedback_date_col", lang)
                            feedback_log_df[feedback_date_col_name] = pd.to_datetime(feedback_log_df[feedback_date_col_name], errors='coerce').dt.date
                        
                            freediver_options_editor = all_known_users_list 
                            instructor_options_editor_feedback = sorted([user for user, profile in user_profiles.items() if profile.get("certification") in INSTRUCTOR_CERT_LEVELS_FOR_ADMIN_TABS_AND_DROPDOWNS])
                            if not instructor_options_editor_feedback: instructor_options_editor_feedback = [_("select_instructor_prompt", lang)]
                            training_options_editor_map_feedback = {log['id']: f"{log['date']} - {log['place']}" for log in sorted(training_log_loaded, key=lambda x: x['date'], reverse=True)}
                            training_options_editor_display_with_none_feedback = [_("select_training_prompt", lang)] + list(training_options_editor_map_feedback.values())

                            edited_feedback_log_df = st.data_editor(
                                feedback_log_df,
                                column_config={
                                    "id": None, "training_session_id_hidden": None,
                                    _("feedback_date_col", lang): st.column_config.DateColumn(label=_("feedback_date_col", lang), format="YYYY-MM-DD", required=True),
                                    _("feedback_for_freediver_label", lang): st.column_config.SelectboxColumn(label=_("feedback_for_freediver_label", lang), options=freediver_options_editor, required=True), 
                                    _("instructor_name_label", lang): st.column_config.SelectboxColumn(label=_("instructor_name_label", lang), options=instructor_options_editor_feedback, required=True),
                                    _("training_session_label", lang): st.column_config.SelectboxColumn(label=_("training_session_label", lang), options=training_options_editor_display_with_none_feedback, required=False),
                                    _("feedback_text_label", lang): st.column_config.TextColumn(label=_("feedback_text_label", lang), required=True),
                                    _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(label=_("history_delete_col_editor", lang), default=False)},
                                hide_index=True, key="feedback_log_data_editor_sub", num_rows="dynamic"
                            )
                            if st.button(_("save_feedback_log_changes_button", lang), key="save_feedback_log_changes_sub"):
                                feedback_log_changes_made = False
                                temp_feedback_log = [fb_loop.copy() for fb_loop in instructor_feedback_loaded]
                                newly_added_feedbacks = []
                                for edited_row_data in edited_feedback_log_df.to_dict(orient="records"):
                                    feedback_id = edited_row_data.get("id")
                                    is_new_feedback_row = feedback_id is None
                                    if is_new_feedback_row: feedback_id = uuid.uuid4().hex; edited_row_data["id"] = feedback_id
                                    if edited_row_data[_("history_delete_col_editor", lang)] and not is_new_feedback_row:
                                        temp_feedback_log = [fb_loop for fb_loop in temp_feedback_log if fb_loop.get("id") != feedback_id]
                                        feedback_log_changes_made = True; continue
                                    edited_fb_date_obj = edited_row_data[_("feedback_date_col", lang)]
                                    edited_fb_date_str = edited_fb_date_obj.isoformat() if isinstance(edited_fb_date_obj, date) else str(edited_fb_date_obj)
                                    edited_freediver = edited_row_data[_("feedback_for_freediver_label", lang)] 
                                    edited_instructor_name_feedback = edited_row_data[_("instructor_name_label", lang)]
                                    edited_training_session_display = edited_row_data[_("training_session_label", lang)]
                                    edited_feedback_text = edited_row_data[_("feedback_text_label", lang)].strip()
                                    edited_training_id = None
                                    if edited_training_session_display != _("select_training_prompt", lang):
                                        for log_id_map, display_str_map in training_options_editor_map_feedback.items():
                                            if display_str_map == edited_training_session_display: edited_training_id = log_id_map; break
                                    if not edited_freediver or edited_freediver == _("select_freediver_prompt", lang) or \
                                       not edited_instructor_name_feedback or edited_instructor_name_feedback == _("select_instructor_prompt", lang) or \
                                       not edited_feedback_text:
                                        st.error(f"Missing required fields for feedback (ID: {feedback_id if feedback_id else 'New'}). Skipping."); continue
                                    if is_new_feedback_row:
                                        newly_added_feedbacks.append({"id": feedback_id, "feedback_date": edited_fb_date_str, "diver_name": edited_freediver, "training_session_id": edited_training_id, "instructor_name": edited_instructor_name_feedback, "feedback_text": edited_feedback_text}) 
                                        feedback_log_changes_made = True
                                    else:
                                        original_fb_index = next((i for i, fb_item_loop in enumerate(temp_feedback_log) if fb_item_loop.get("id") == feedback_id), -1)
                                        if original_fb_index != -1:
                                            original_fb_data = temp_feedback_log[original_fb_index]
                                            if (original_fb_data.get('feedback_date') != edited_fb_date_str or original_fb_data.get('diver_name') != edited_freediver or 
                                                original_fb_data.get('instructor_name') != edited_instructor_name_feedback or original_fb_data.get('training_session_id') != edited_training_id or
                                                original_fb_data.get('feedback_text') != edited_feedback_text):
                                                temp_feedback_log[original_fb_index].update({"feedback_date": edited_fb_date_str, "diver_name": edited_freediver, "instructor_name": edited_instructor_name_feedback, "training_session_id": edited_training_id, "feedback_text": edited_feedback_text}) 
                                                feedback_log_changes_made = True
                                if feedback_log_changes_made:
                                    instructor_feedback_loaded[:] = temp_feedback_log + newly_added_feedbacks
                                    save_instructor_feedback(instructor_feedback_loaded)
                                    st.success(_("feedback_log_updated_success", lang)); st.rerun()
                                else: st.info("No changes detected in the feedback log.")

        if tab_club_performances_view:
            with tab_club_performances_view:
                if not all_records_loaded: st.info(_("no_ranking_data", lang))
                else:
                    with st.container(border=True):
                        st.subheader(_("club_bests_subheader", lang))
                        club_pbs = {}
                        for disc_key_club_pb in discipline_keys:
                            club_disc_records = [r for r in all_records_loaded if r['discipline'] == disc_key_club_pb and r.get('parsed_value') is not None]
                            if not club_disc_records: club_pbs[disc_key_club_pb] = ("N/A", None, None, None); continue
                            best_club_record = min(club_disc_records, key=lambda x: x['parsed_value']) if disc_key_club_pb == "16x25m Speed Endurance" else max(club_disc_records, key=lambda x: x['parsed_value'])
                            club_pb_value_formatted = format_seconds_to_static_time(best_club_record['parsed_value']) if is_time_based_discipline(disc_key_club_pb) else f"{best_club_record['parsed_value']}m"
                            club_pbs[disc_key_club_pb] = (club_pb_value_formatted, best_club_record['user'], best_club_record.get('event_name', "N/A"), best_club_record.get('event_date', "N/A"))

                        cols_club_pb = st.columns(len(discipline_keys))
                        for i, disc_key_club_pb_col in enumerate(discipline_keys):
                            val_club, user_club, event_name_club, event_date_club = club_pbs.get(disc_key_club_pb_col, ("N/A", None, None, None))
                            with cols_club_pb[i]:
                                translated_full_disc_name_club = _("disciplines." + disc_key_club_pb_col, lang)
                                short_disc_name_club = translated_full_disc_name_club.split('(')[0].strip() or translated_full_disc_name_club
                                display_user_club = get_display_name(user_club, user_profiles, lang) if user_club else _("anonymous_freediver_name", lang) 
                                st.metric(label=_("club_best_label", lang, discipline_short_name=short_disc_name_club), value=val_club)
                                if user_club and event_date_club and event_date_club != "N/A":
                                    st.caption(_("achieved_at_event_on_date_caption", lang, user=display_user_club, event_name=event_name_club, event_date=event_date_club))
                                elif val_club == "N/A": st.caption(_("no_record_yet_caption", lang))

                    st.markdown("")
                    
                    ranking_sub_tab_titles = [_("disciplines." + key, lang) for key in discipline_keys]
                    ranking_sub_tabs = st.tabs(ranking_sub_tab_titles)
                    for i_rank_sub_tab, selected_discipline_ranking_key in enumerate(discipline_keys):
                        with ranking_sub_tabs[i_rank_sub_tab]:
                            user_pbs_for_discipline_ranking = []
                            for u_rank_tab in all_known_users_list:
                                user_specific_discipline_records_ranking = [r_rank_tab for r_rank_tab in all_records_loaded if r_rank_tab['user'] == u_rank_tab and r_rank_tab['discipline'] == selected_discipline_ranking_key and r_rank_tab.get('parsed_value') is not None]
                                if user_specific_discipline_records_ranking:
                                    best_record_for_user_ranking = min(user_specific_discipline_records_ranking, key=lambda x_rank_tab: x_rank_tab['parsed_value']) if selected_discipline_ranking_key == "16x25m Speed Endurance" else max(user_specific_discipline_records_ranking, key=lambda x_rank_tab: x_rank_tab['parsed_value'])
                                    user_pbs_for_discipline_ranking.append({"user": u_rank_tab, "parsed_value": best_record_for_user_ranking['parsed_value'], "event_date": best_record_for_user_ranking.get('event_date'), "event_name": best_record_for_user_ranking.get('event_name'), "original_performance_str": best_record_for_user_ranking.get('original_performance_str')})
                            
                            sort_reverse_ranking = selected_discipline_ranking_key != "16x25m Speed Endurance"
                            sorted_rankings_tab = sorted(user_pbs_for_discipline_ranking, key=lambda x_sort_tab: x_sort_tab['parsed_value'], reverse=sort_reverse_ranking)

                            if not sorted_rankings_tab: st.info(_("no_ranking_data", lang))
                            else:
                                st.subheader(_("podium_header", lang))
                                podium_data = {1: [], 2: [], 3: []}
                                distinct_podium_performances = []
                                if sorted_rankings_tab:
                                    temp_distinct_perfs = [sorted_rankings_tab[0]['parsed_value']]
                                    for p_entry in sorted_rankings_tab:
                                        if p_entry['parsed_value'] != temp_distinct_perfs[-1] and len(temp_distinct_perfs) < 3: temp_distinct_perfs.append(p_entry['parsed_value'])
                                        elif len(temp_distinct_perfs) >=3: break
                                    distinct_podium_performances = temp_distinct_perfs
                                for place_idx, place_perf_val in enumerate(distinct_podium_performances):
                                    if place_idx < 3: podium_data[place_idx+1] = sorted([p for p in sorted_rankings_tab if p['parsed_value'] == place_perf_val], key=lambda x: x.get('event_date', '1900-01-01')) 
                                
                                podium_cols = st.columns(3)
                                medal_emojis = ["🥇", "🥈", "🥉"]
                                for i_podium in range(3):
                                    with podium_cols[i_podium]:
                                        place = i_podium + 1
                                        if podium_data[place]:
                                            st.markdown(f"<h3 style='text-align: center;'>{medal_emojis[i_podium]}</h3>", unsafe_allow_html=True)
                                            for rank_entry in podium_data[place]:
                                                perf_display = format_seconds_to_static_time(rank_entry['parsed_value']) if is_time_based_discipline(selected_discipline_ranking_key) else f"{rank_entry['parsed_value']}m"
                                                display_name_podium = get_display_name(rank_entry['user'], user_profiles, lang)
                                                st.markdown(f"<div style='text-align: center; border: 1px solid #eee; border-radius: 8px; padding: 8px; margin-bottom: 8px; background-color: #f9f9f9;'><h5>{display_name_podium}</h5><h6>{perf_display}</h6><p style='font-size: 0.8em;'>{rank_entry.get('event_name','')} - {rank_entry.get('event_date','')}</p></div>", unsafe_allow_html=True)
                                        else: st.markdown(f"<div style='text-align: center; opacity: 0.5;'><h3>{medal_emojis[i_podium]}</h3><h4>-</h4><p style='font-size: 0.8em;'>&nbsp;</p></div>", unsafe_allow_html=True)

                                st.markdown("")
                                st.subheader(_("full_ranking_header", lang))
                                ranking_table_data_tab = []
                                for rank_idx_tab, rank_item_tab in enumerate(sorted_rankings_tab):
                                    perf_display_table_tab = format_seconds_to_static_time(rank_item_tab['parsed_value']) if is_time_based_discipline(selected_discipline_ranking_key) else f"{rank_item_tab['parsed_value']}m"
                                    ranking_table_data_tab.append({
                                        _("rank_col", lang): rank_idx_tab + 1,
                                        _("user_col", lang): get_display_name(rank_item_tab['user'], user_profiles, lang),
                                        _("best_performance_col", lang): perf_display_table_tab,
                                        _("event_col", lang): rank_item_tab.get('event_name', "N/A"),
                                        _("date_achieved_col", lang): rank_item_tab.get('event_date', "N/A")}) 
                                ranking_df_tab = pd.DataFrame(ranking_table_data_tab)
                                st.dataframe(ranking_df_tab, use_container_width=True, hide_index=True)

                                st.markdown("")
                                st.subheader(_("certification_stats_header", lang))
                                data_for_stats = []
                                for item_stat in user_pbs_for_discipline_ranking:
                                    user_profile_stat = user_profiles.get(item_stat['user'], {})
                                    certification_stat = user_profile_stat.get("certification", _("no_certification_option", lang))
                                    data_for_stats.append({"certification": certification_stat, "parsed_value": item_stat['parsed_value']})
                                if not data_for_stats: st.info(_("no_stats_data", lang))
                                else:
                                    stats_df = pd.DataFrame(data_for_stats)
                                    stats_df['parsed_value'] = pd.to_numeric(stats_df['parsed_value'])
                                    
                                    certification_summary = stats_df.groupby('certification')['parsed_value'].agg(
                                        min_perf='min', 
                                        max_perf='max', 
                                        avg_perf='mean'
                                    ).reset_index() 

                                    is_time_discipline_for_stats = is_time_based_discipline(selected_discipline_ranking_key)
                                    
                                    def format_perf_value_for_stats(value, is_time_based):
                                        if pd.isna(value): return "N/A"
                                        if is_time_based: return format_seconds_to_static_time(value)
                                        else: 
                                            if isinstance(value, float) and value.is_integer(): return f"{int(value)}m"
                                            elif isinstance(value, float): return f"{value:.1f}m" 
                                            return f"{int(value)}m" 

                                    certification_summary_renamed = certification_summary.rename(columns={'certification': _("certification_level_col", lang)})
                                    certification_summary_renamed[_("min_performance_col", lang)] = certification_summary_renamed['min_perf'].apply(lambda x: format_perf_value_for_stats(x, is_time_discipline_for_stats))
                                    certification_summary_renamed[_("max_performance_col", lang)] = certification_summary_renamed['max_perf'].apply(lambda x: format_perf_value_for_stats(x, is_time_discipline_for_stats))
                                    certification_summary_renamed[_("avg_performance_col", lang)] = certification_summary_renamed['avg_perf'].apply(lambda x: format_perf_value_for_stats(x, is_time_discipline_for_stats))
                                    
                                    display_cols = [_("certification_level_col", lang), _("min_performance_col", lang), _("max_performance_col", lang), _("avg_performance_col", lang)]
                                    final_display_cols = [col for col in display_cols if col in certification_summary_renamed.columns] 
                                    display_stats_df = certification_summary_renamed[final_display_cols]
                                    
                                    if display_stats_df.empty: st.info(_("no_stats_data", lang))
                                    else: st.dataframe(display_stats_df, use_container_width=True, hide_index=True)
                                
                                st.markdown("---")
                                st.subheader(_("club_performances_tab_title", lang)) 
                                club_discipline_records_graph = [r for r in all_records_loaded if r['discipline'] == selected_discipline_ranking_key and r.get('parsed_value') is not None and r.get('event_date')]
                                if not club_discipline_records_graph: st.caption(_("no_data_for_club_performance_display", lang))
                                else:
                                    df_club_discipline_graph_data = [{'event_date': pd.to_datetime(r_club['event_date']), 'parsed_value': r_club['parsed_value'], 'user': get_display_name(r_club['user'], user_profiles, lang), 'event_name': r_club.get('event_name','N/A'), 'original_performance_str': r_club['original_performance_str']} for r_club in club_discipline_records_graph]
                                    df_club_discipline_graph = pd.DataFrame(df_club_discipline_graph_data)
                                    y_title_graph = _("performance_value", lang) + (f" ({_('seconds_unit', lang)})" if is_time_based_discipline(selected_discipline_ranking_key) else f" ({_('meters_unit', lang)})")
                                    x_title_graph = _("history_event_date_col", lang) 
                                    
                                    individual_lines_graph = alt.Chart(df_club_discipline_graph).mark_line(point=True).encode(
                                        x=alt.X('event_date:T', title=x_title_graph), 
                                        y=alt.Y('parsed_value:Q', title=y_title_graph), 
                                        color='user:N', 
                                        tooltip=['user:N', alt.Tooltip('event_date:T', title=x_title_graph), 'original_performance_str:N', 'event_name:N']
                                    ).interactive()
                                    
                                    df_club_discipline_for_avg_graph = df_club_discipline_graph.set_index('event_date'); quarterly_avg_df_graph = df_club_discipline_for_avg_graph['parsed_value'].resample('QE').mean().reset_index(); quarterly_avg_df_graph.columns = ['event_date', 'average_performance']
                                    if not quarterly_avg_df_graph.empty:
                                        average_line_graph = alt.Chart(quarterly_avg_df_graph).mark_line(color='black', strokeDash=[5,5], size=2).encode(
                                            x=alt.X('event_date:T', title=x_title_graph), 
                                            y=alt.Y('average_performance:Q', title=y_title_graph), 
                                            tooltip=[alt.Tooltip('event_date:T', title=x_title_graph, format='%Y-%m'), alt.Tooltip('average_performance:Q', title=_("quarterly_average_label", lang), format=".2f" if not is_time_based_discipline(selected_discipline_ranking_key) else "")]
                                        )
                                        combined_chart_graph = alt.layer(individual_lines_graph, average_line_graph).resolve_scale(y='shared')
                                        st.altair_chart(combined_chart_graph, use_container_width=True)
                                    else: st.altair_chart(individual_lines_graph, use_container_width=True); st.caption("Not enough data for quarterly average.")
        
        if is_admin_view_authorized and tab_freedivers: 
            with tab_freedivers: 
                cert_order = ["I3", "I2", "I1", "S4", "A3", "A2", "A1", "NB", _("no_certification_option", lang)]; cert_order_map = {level: i for i, level in enumerate(cert_order)}
                
                st.subheader(_("edit_freedivers_header", lang))

                freedivers_data_for_editor = [] 
                for user_name in all_known_users_list:
                    profile = user_profiles.get(user_name, {}); certification = profile.get("certification", _("no_certification_option", lang)); cert_date_str = profile.get("certification_date"); cert_date_obj = None
                    if cert_date_str: 
                        try: cert_date_obj = date.fromisoformat(cert_date_str)
                        except (ValueError, TypeError): pass
                    lifras_id = profile.get("lifras_id", ""); anonymize = profile.get("anonymize_results", False)
                    user_pbs_display = {}
                    for disc_key in discipline_keys:
                        user_disc_records = [r for r in all_records_loaded if r['user'] == user_name and r['discipline'] == disc_key and r.get('parsed_value') is not None]
                        if user_disc_records:
                            best_record = min(user_disc_records, key=lambda x: x['parsed_value']) if disc_key == "16x25m Speed Endurance" else max(user_disc_records, key=lambda x: x['parsed_value'])
                            user_pbs_display[disc_key] = format_seconds_to_static_time(best_record['parsed_value']) if is_time_based_discipline(disc_key) else f"{best_record['parsed_value']}m"
                        else: user_pbs_display[disc_key] = "N/A"
                    freedivers_data_for_editor.append({ 
                        _("original_name_col_editor_hidden", lang): user_name, _("freediver_name_col_editor", lang): user_name, _("certification_col_editor", lang): certification, 
                        _("certification_date_col_editor", lang): cert_date_obj, _("lifras_id_col_editor", lang): lifras_id, _("anonymize_results_col_editor", lang): anonymize,
                        _("pb_sta_col_editor", lang): user_pbs_display.get("Static Apnea (STA)", "N/A"), _("pb_dynbf_col_editor", lang): user_pbs_display.get("Dynamic Bi-fins (DYN-BF)", "N/A"),
                        _("pb_depth_col_editor", lang): user_pbs_display.get("Depth (CWT/FIM)", "N/A"), _("pb_vwt_nlt_col_editor", lang): user_pbs_display.get("Profondeur (VWT/NLT)", "N/A"),
                        _("pb_16x25_col_editor", lang): user_pbs_display.get("16x25m Speed Endurance", "N/A"),
                    })
                def sort_freedivers(freediver_entry): 
                    cert_level = freediver_entry[_("certification_col_editor", lang)]; cert_date_val = freediver_entry[_("certification_date_col_editor", lang)]
                    sortable_cert_date = cert_date_val if cert_date_val is not None else date.min
                    return (cert_order_map.get(cert_level, len(cert_order)), sortable_cert_date)
                sorted_freedivers_data = sorted(freedivers_data_for_editor, key=sort_freedivers) 
                freedivers_df = pd.DataFrame(sorted_freedivers_data) 
                cert_options_for_editor = [_("no_certification_option", lang)] + list(_("certification_levels", lang).keys())
                column_config_freedivers = { 
                    _("original_name_col_editor_hidden", lang): None,
                    _("freediver_name_col_editor", lang): st.column_config.TextColumn(label=_("freediver_name_col_editor", lang), required=True), 
                    _("certification_col_editor", lang): st.column_config.SelectboxColumn(label=_("certification_col_editor", lang), options=cert_options_for_editor, required=False),
                    _("certification_date_col_editor", lang): st.column_config.DateColumn(label=_("certification_date_col_editor", lang), format="YYYY-MM-DD"),
                    _("lifras_id_col_editor", lang): st.column_config.TextColumn(label=_("lifras_id_col_editor", lang)),
                    _("anonymize_results_col_editor", lang): st.column_config.CheckboxColumn(label=_("anonymize_results_col_editor", lang), default=False),
                    _("pb_sta_col_editor", lang): st.column_config.TextColumn(label=_("pb_sta_col_editor", lang), disabled=True),
                    _("pb_dynbf_col_editor", lang): st.column_config.TextColumn(label=_("pb_dynbf_col_editor", lang), disabled=True),
                    _("pb_depth_col_editor", lang): st.column_config.TextColumn(label=_("pb_depth_col_editor", lang), disabled=True),
                    _("pb_vwt_nlt_col_editor", lang): st.column_config.TextColumn(label=_("pb_vwt_nlt_col_editor", lang), disabled=True),
                    _("pb_16x25_col_editor", lang): st.column_config.TextColumn(label=_("pb_16x25_col_editor", lang), disabled=True),
                }
                edited_freedivers_df = st.data_editor(freedivers_df, column_config=column_config_freedivers, key="freedivers_data_editor", num_rows="dynamic", hide_index=True) 
                
                if st.button(_("save_freedivers_changes_button", lang), key="save_freedivers_changes"):
                    changes_made = False
                    
                    # Get original and edited names
                    original_names = set(freedivers_df[_("original_name_col_editor_hidden", lang)])
                    edited_df_rows = edited_freedivers_df.to_dict(orient='records')
                    edited_names_from_editor = {row[_("freediver_name_col_editor", lang)].strip() for row in edited_df_rows if row[_("freediver_name_col_editor", lang)] and str(row[_("freediver_name_col_editor", lang)]).strip()}

                    # --- 1. Handle Deletions ---
                    deleted_names = original_names - edited_names_from_editor
                    if deleted_names:
                        changes_made = True
                        for name_to_delete in deleted_names:
                            user_profiles.pop(name_to_delete, None)
                            all_records_loaded = [r for r in all_records_loaded if r.get('user') != name_to_delete]
                            instructor_feedback_loaded = [f for f in instructor_feedback_loaded if f.get('diver_name') != name_to_delete and f.get('instructor_name') != name_to_delete]
                            if st.session_state.get('current_user') == name_to_delete:
                                st.session_state.current_user = None

                    # --- 2. Handle Additions and Updates ---
                    name_update_map = {}
                    current_names_in_db = set(user_profiles.keys())

                    # Check for duplicate names in the editor before processing
                    all_edited_names_list = [str(row[_("freediver_name_col_editor", lang)]).strip() for row in edited_df_rows if row[_("freediver_name_col_editor", lang)]]
                    if len(all_edited_names_list) != len(set(all_edited_names_list)):
                        st.error("Erreur : Des noms en double ont été trouvés dans le tableau. Veuillez vous assurer que tous les noms d'apnéistes sont uniques.")
                        st.stop()

                    for row in edited_df_rows:
                        original_name = row[_("original_name_col_editor_hidden", lang)]
                        new_name = str(row[_("freediver_name_col_editor", lang)]).strip()
                        
                        if not new_name:
                            st.warning("Ligne avec un nom vide ignorée.")
                            continue
                            
                        is_new_row = pd.isna(original_name)

                        if is_new_row:
                            if new_name in current_names_in_db:
                                st.error(_("freediver_name_conflict_error", lang, new_name=new_name))
                                continue
                            
                            changes_made = True
                            user_profiles[new_name] = {
                                "certification": row[_("certification_col_editor", lang)],
                                "certification_date": row[_("certification_date_col_editor", lang)].isoformat() if pd.notna(row[_("certification_date_col_editor", lang)]) else None,
                                "lifras_id": str(row[_("lifras_id_col_editor", lang)]).strip(),
                                "anonymize_results": bool(row[_("anonymize_results_col_editor", lang)])
                            }
                            current_names_in_db.add(new_name)
                        else:
                            name_changed = (original_name != new_name)
                            if name_changed and new_name in current_names_in_db:
                                st.error(_("freediver_name_conflict_error", lang, new_name=new_name))
                                continue

                            profile = user_profiles.get(original_name, {})
                            new_cert_date = row[_("certification_date_col_editor", lang)]
                            new_cert_date_str = new_cert_date.isoformat() if pd.notna(new_cert_date) and isinstance(new_cert_date, date) else None
                            
                            if (name_changed or
                                profile.get("certification") != row[_("certification_col_editor", lang)] or
                                profile.get("certification_date") != new_cert_date_str or
                                profile.get("lifras_id", "") != str(row[_("lifras_id_col_editor", lang)]).strip() or
                                profile.get("anonymize_results", False) != bool(row[_("anonymize_results_col_editor", lang)])):
                                
                                changes_made = True
                                profile_data = user_profiles.pop(original_name, {})
                                profile_data.update({
                                    "certification": row[_("certification_col_editor", lang)],
                                    "certification_date": new_cert_date_str,
                                    "lifras_id": str(row[_("lifras_id_col_editor", lang)]).strip(),
                                    "anonymize_results": bool(row[_("anonymize_results_col_editor", lang)])
                                })
                                user_profiles[new_name] = profile_data
                                
                                if name_changed:
                                    name_update_map[original_name] = new_name
                                    current_names_in_db.discard(original_name)
                                    current_names_in_db.add(new_name)

                    if name_update_map:
                        changes_made = True
                        for record in all_records_loaded:
                            if record.get('user') in name_update_map:
                                record['user'] = name_update_map[record['user']]
                        for feedback in instructor_feedback_loaded:
                            if feedback.get('diver_name') in name_update_map:
                                feedback['diver_name'] = name_update_map[feedback['diver_name']]
                            if feedback.get('instructor_name') in name_update_map:
                                feedback['instructor_name'] = name_update_map[feedback['instructor_name']]
                        
                        if st.session_state.get('current_user') in name_update_map:
                            st.session_state.current_user = name_update_map[st.session_state.current_user]

                    if changes_made:
                        save_user_profiles(user_profiles)
                        save_records(all_records_loaded)
                        save_instructor_feedback(instructor_feedback_loaded)
                        st.success(_("freedivers_updated_success", lang))
                        st.rerun()
                    else:
                        st.info("Aucun changement détecté dans les données des apnéistes.")
                
                st.markdown("---"); st.subheader(_("freediver_certification_summary_header", lang)) 
                cert_counts = {}
                for profile in user_profiles.values(): cert_level = profile.get("certification", _("no_certification_option", lang)); cert_counts[cert_level] = cert_counts.get(cert_level, 0) + 1
                if not cert_counts: st.info(_("no_stats_data", lang))
                else: summary_data = [{_("certification_level_col", lang): level, _("count_col", lang): count} for level, count in cert_counts.items()]; summary_df = pd.DataFrame(summary_data); st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        if is_admin_view_authorized and main_training_log_tab_obj:
            with main_training_log_tab_obj:
                sub_tab_training_sessions_label = _("training_sessions_sub_tab_label", lang); sub_tab_edit_training_sessions_label = _("edit_training_sessions_sub_tab_label", lang)
                training_sub_tab1, training_sub_tab2 = st.tabs([sub_tab_training_sessions_label, sub_tab_edit_training_sessions_label])
                with training_sub_tab1:
                    st.subheader(_("detailed_training_sessions_subheader", lang))
                    if not training_log_loaded: st.info(_("no_training_sessions_logged", lang))
                    else:
                        for entry in sorted(training_log_loaded, key=lambda x: x.get('date', '1900-01-01'), reverse=True):
                            expander_title = f"**{entry.get('date', 'N/A')} | {entry.get('place', 'N/A')}**"
                            with st.expander(expander_title): st.markdown(entry.get('description', _("no_description_available", lang)))
                with training_sub_tab2:
                    st.subheader(_("training_log_table_header", lang))
                    if not training_log_loaded: st.info(_("no_training_sessions_logged", lang))
                    else:
                        training_log_display = [{"id": entry.get("id"), _("training_date_label", lang): entry.get("date"), _("training_place_label", lang): entry.get("place"), _("training_description_label", lang): entry.get("description"), _("history_delete_col_editor", lang): False} for entry in sorted(training_log_loaded, key=lambda x: x['date'], reverse=True)]
                        training_df_for_editor = pd.DataFrame(training_log_display)
                        if not training_df_for_editor.empty:
                            training_date_col_name = _("training_date_label", lang)
                            training_df_for_editor[training_date_col_name] = pd.to_datetime(training_df_for_editor[training_date_col_name], errors='coerce').dt.date
                            edited_training_df = st.data_editor(
                                training_df_for_editor,
                                column_config={"id": None, _("training_date_label", lang): st.column_config.DateColumn(label=_("training_date_label", lang), format="YYYY-MM-DD"), _("training_place_label", lang): st.column_config.TextColumn(label=_("training_place_label", lang)), _("training_description_label", lang): st.column_config.TextColumn(label=_("training_description_label", lang)), _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(label=_("history_delete_col_editor", lang), default=False)},
                                hide_index=True, key="training_log_editor_sub", num_rows="dynamic"
                            )
                            if st.button(_("save_training_log_changes_button", lang), key="save_training_log_changes_sub"):
                                training_changes_made = False; temp_training_log_loaded = [log.copy() for log in training_log_loaded]
                                for index, edited_row_series in edited_training_df.iterrows():
                                    edited_row = edited_row_series.to_dict(); log_id = edited_row.get("id"); 
                                    if log_id is None: continue
                                    original_log_index = next((i for i, log_item in enumerate(temp_training_log_loaded) if log_item.get("id") == log_id), -1)
                                    if original_log_index == -1: continue
                                    if edited_row[_("history_delete_col_editor", lang)]: del temp_training_log_loaded[original_log_index]; training_changes_made = True; continue
                                    edited_log_date_obj = edited_row[_("training_date_label", lang)]; edited_log_date_str = edited_log_date_obj.isoformat() if isinstance(edited_log_date_obj, date) else str(edited_log_date_obj)
                                    if (temp_training_log_loaded[original_log_index]['date'] != edited_log_date_str or temp_training_log_loaded[original_log_index]['place'] != edited_row[_("training_place_label", lang)] or temp_training_log_loaded[original_log_index]['description'] != edited_row[_("training_description_label", lang)]):
                                        temp_training_log_loaded[original_log_index].update({'date': edited_log_date_str, 'place': edited_row[_("training_place_label", lang)], 'description': edited_row[_("training_description_label", lang)]}); training_changes_made = True
                                if training_changes_made:
                                    training_log_loaded[:] = temp_training_log_loaded; save_training_log(training_log_loaded)
                                    st.success(_("training_log_updated_success", lang)); st.rerun()
                                else: st.info("No changes detected in the training log.")
        
        if is_admin_view_authorized and tab_performance_log:
            with tab_performance_log:
                if not all_records_loaded: 
                    st.info("No performances logged yet in the system.")
                else:
                    all_perf_display_list = []
                    for rec in sorted(all_records_loaded, key=lambda x: x.get('entry_date', '1900-01-01'), reverse=True): 
                        all_perf_display_list.append({
                            "id": rec.get("id"),
                            _("history_event_name_col", lang): rec.get("event_name", "N/A"),
                            _("history_event_date_col", lang): rec.get("event_date"),
                            _("history_entry_date_col", lang): rec.get("entry_date"), 
                            _("user_col", lang): rec.get("user"),
                            _("history_discipline_col", lang): rec.get("discipline"),
                            _("history_performance_col", lang): rec.get("original_performance_str", ""),
                            _("history_delete_col_editor", lang): False
                        })
                    all_perf_df_for_editor = pd.DataFrame(all_perf_display_list)
                    if not all_perf_df_for_editor.empty:
                        col_event_date_log = _("history_event_date_col", lang)
                        col_entry_date_log = _("history_entry_date_col", lang)
                        all_perf_df_for_editor[col_event_date_log] = pd.to_datetime(all_perf_df_for_editor[col_event_date_log], errors='coerce').dt.date
                        all_perf_df_for_editor[col_entry_date_log] = pd.to_datetime(all_perf_df_for_editor[col_entry_date_log], errors='coerce').dt.date
                    
                        edited_all_perf_df = st.data_editor(
                            all_perf_df_for_editor,
                            column_config={
                                "id": None,
                                _("history_event_name_col", lang): st.column_config.TextColumn(label=_("history_event_name_col", lang), required=True),
                                _("history_event_date_col", lang): st.column_config.DateColumn(label=_("history_event_date_col", lang), format="YYYY-MM-DD", required=True),
                                _("history_entry_date_col", lang): st.column_config.DateColumn(label=_("history_entry_date_col", lang), format="YYYY-MM-DD", disabled=True), 
                                _("user_col", lang): st.column_config.TextColumn(label=_("user_col", lang), required=True),
                                _("history_discipline_col", lang): st.column_config.SelectboxColumn(label=_("history_discipline_col", lang), options=discipline_keys, required=True),
                                _("history_performance_col", lang): st.column_config.TextColumn(label=_("history_performance_col", lang), required=True),
                                _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(label=_("history_delete_col_editor", lang), default=False)},
                            hide_index=True, key="all_performances_data_editor", num_rows="dynamic"
                        )
                        if st.button(_("save_all_performances_button", lang), key="save_all_perf_changes"):
                            changes_made_all_perf = False; temp_master_records = [r.copy() for r in all_records_loaded]; newly_added_records_from_editor = []
                            for edited_row_data in edited_all_perf_df.to_dict(orient="records"):
                                record_id = edited_row_data.get("id"); is_new_row = record_id is None
                                if is_new_row: record_id = uuid.uuid4().hex; edited_row_data["id"] = record_id
                                if edited_row_data[_("history_delete_col_editor", lang)] and not is_new_row:
                                    temp_master_records = [r for r in temp_master_records if r.get("id") != record_id]; changes_made_all_perf = True; continue
                                
                                edited_user = edited_row_data[_("user_col", lang)].strip()
                                edited_event_name = edited_row_data[_("history_event_name_col", lang)].strip()
                                edited_event_date_obj = edited_row_data[_("history_event_date_col", lang)]
                                edited_discipline_key = edited_row_data[_("history_discipline_col", lang)]
                                edited_perf_str = str(edited_row_data[_("history_performance_col", lang)]).strip()
                                
                                edited_event_date_str = None
                                if isinstance(edited_event_date_obj, date): edited_event_date_str = edited_event_date_obj.isoformat()
                                elif isinstance(edited_event_date_obj, str): 
                                    try: edited_event_date_str = date.fromisoformat(edited_event_date_obj).isoformat()
                                    except ValueError: st.error(f"Invalid event date format '{edited_event_date_obj}' for user {edited_user}. Skipping."); continue
                                else: st.error(f"Invalid event date provided for user {edited_user}. Skipping."); continue

                                if not edited_user or not edited_event_name or not edited_discipline_key or not edited_perf_str or not edited_event_date_str:
                                    st.error(f"Missing data for one of the records. Skipping."); continue
                                
                                parsed_value = parse_static_time_to_seconds(edited_perf_str, lang) if is_time_based_discipline(edited_discipline_key) else parse_distance_to_meters(edited_perf_str, lang)
                                if parsed_value is None: st.error(f"Invalid performance format for '{edited_perf_str}'. Skipping."); continue

                                current_entry_date = date.today().isoformat() 
                                linked_session_id_to_save = None 

                                if not is_new_row:
                                    original_record_for_updates = next((r for r in temp_master_records if r.get("id") == record_id), None)
                                    if original_record_for_updates:
                                        current_entry_date = original_record_for_updates.get('entry_date', current_entry_date)
                                        linked_session_id_to_save = original_record_for_updates.get('linked_training_session_id') 


                                if is_new_row:
                                    newly_added_records_from_editor.append({
                                        "id": record_id, "user": edited_user, "event_name": edited_event_name, "event_date": edited_event_date_str, 
                                        "entry_date": current_entry_date, "discipline": edited_discipline_key, 
                                        "original_performance_str": edited_perf_str, "parsed_value": parsed_value,
                                        "linked_training_session_id": linked_session_id_to_save 
                                    })
                                    changes_made_all_perf = True
                                    if edited_user not in user_profiles: user_profiles[edited_user] = {"certification": _("no_certification_option", lang), "certification_date": None, "lifras_id": "", "anonymize_results": False}
                                else:
                                    original_record_index = next((i for i, r_item in enumerate(temp_master_records) if r_item.get("id") == record_id), -1)
                                    if original_record_index != -1:
                                        original_rec_data = temp_master_records[original_record_index]
                                        if (original_rec_data.get('event_name') != edited_event_name or original_rec_data.get('event_date') != edited_event_date_str or
                                            original_rec_data.get('user') != edited_user or original_rec_data.get('discipline') != edited_discipline_key or
                                            original_rec_data.get('original_performance_str') != edited_perf_str):
                                            temp_master_records[original_record_index].update({
                                                'event_name': edited_event_name, 'event_date': edited_event_date_str, 'user': edited_user, 
                                                'discipline': edited_discipline_key, 'original_performance_str': edited_perf_str, 'parsed_value': parsed_value
                                            })
                                            changes_made_all_perf = True
                                            if edited_user not in user_profiles: user_profiles[edited_user] = {"certification": _("no_certification_option", lang), "certification_date": None, "lifras_id": "", "anonymize_results": False}
                            if changes_made_all_perf:
                                all_records_loaded[:] = temp_master_records + newly_added_records_from_editor
                                save_records(all_records_loaded); save_user_profiles(user_profiles) 
                                st.success(_("all_performances_updated_success", lang)); st.rerun()
                            else: st.info("No changes detected in all performances.")

if __name__ == "__main__":
    main()
