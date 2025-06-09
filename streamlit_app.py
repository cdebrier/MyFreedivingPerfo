import streamlit as st
import pandas as pd
import json
from datetime import datetime, date, time
import uuid # Added for unique record IDs
import altair as alt # Added for advanced charting
import re

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

# --- Discipline Configuration ---
LOWER_IS_BETTER_DISCIPLINES = ["16x25m Speed Endurance"]

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
        "minutes_unit": "minutes",
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
            "Dynamic No-fins (DNF)": "Dynamic No-fins (DNF)",
            "Depth (CWT/FIM)": "Depth (CWT/FIM)",
            "Profondeur (VWT/NLT)": "Depth (VWT/NLT)",
            "16x25m Speed Endurance": "16x25m Speed Endurance"
        },
        "months": {
            "January": "January", "February": "February", "March": "March", "April": "April", "May": "May", "June": "June", 
            "July": "July", "August": "August", "September": "September", "October": "October", "November": "November", "December": "December"
        },
        "club_performances_overview_tab_label": "🏆 Club Rankings",
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
        "club_level_performance_tab_title": "🏆 Performances by Level",
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
        "pb_dnf_col_editor": "PB DNF",
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
        "performances_overview_tab_label": "📋 Performances",
        "edit_performances_sub_tab_label": "✏️ Edit Performances",
        "save_all_performances_button": "💾 Save Performance Log Changes",
        "all_performances_updated_success": "Performance log updated successfully.",
        "feedback_log_tab_label": "💬 Feedback Log",
        "my_feedback_tab_label": "💬 My Feedback",
        "generate_feedback_summary_button": "Generate Feedback Summary",
        "feedback_summary_header": "Feedback Summary",
        "no_feedback_to_summarize": "No feedback to summarize yet.",
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
        "filter_by_discipline_label": "Filter by Discipline:",
        "all_freedivers_option": "All Freedivers", 
        "all_sessions_option": "All Sessions",
        "all_instructors_option": "All Instructors",
        "all_disciplines_option": "All Disciplines",
        "filter_by_year_label": "Filter by Year:",
        "filter_by_month_label": "Filter by Month:",
        "filter_by_place_label": "Filter by Place:",
        "all_years_option": "All Years",
        "all_months_option": "All Months",
        "all_places_option": "All Places",
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
            "Dynamic No-fins (DNF)": "Dynamique Sans Palmes (DNF)",
            "Depth (CWT/FIM)": "Profondeur (CWT/FIM)",
            "Profondeur (VWT/NLT)": "Profondeur (VWT/NLT)",
            "16x25m Speed Endurance": "16x25m Vitesse Endurance"
        },
        "months": {
            "January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin", 
            "July": "Juillet", "August": "Août", "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"
        },
        "club_performances_overview_tab_label": "🏆 Classements du Club",
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
        "club_level_performance_tab_title": "🏆 Performances par Niveau",
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
        "pb_dnf_col_editor": "RP DNF",
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
        "performances_overview_tab_label": "Vue d'ensemble des Performances",
        "edit_performances_sub_tab_label": "Modifier les Performances",
        "save_all_performances_button": "💾 Sauvegarder les Modifications du Journal",
        "all_performances_updated_success": "Journal des performances mis à jour avec succès.",
        "feedback_log_tab_label": "💬 Journal des Feedbacks", 
        "my_feedback_tab_label": "💬 Mon Feedback",
        "generate_feedback_summary_button": "Générer le résumé des feedbacks",
        "feedback_summary_header": "Résumé des feedbacks",
        "no_feedback_to_summarize": "Aucun feedback à résumer pour le moment.",
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
        "filter_by_discipline_label": "Filtrer par Discipline :",
        "all_freedivers_option": "Tous les Apnéistes", 
        "all_sessions_option": "Toutes les Sessions",
        "all_instructors_option": "Tous les Instructeurs",
        "all_disciplines_option": "Toutes les Disciplines",
        "filter_by_year_label": "Filtrer par Année :",
        "filter_by_month_label": "Filtrer par Mois :",
        "filter_by_place_label": "Filtrer par Lieu :",
        "all_years_option": "Toutes les Années",
        "all_months_option": "Tous les Mois",
        "all_places_option": "Tous les Lieux",
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
        "minutes_unit": "minuten",
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
            "Dynamic No-fins (DNF)": "Dynamisch Zonder Vinnen (DNF)",
            "Depth (CWT/FIM)": "Diepte (CWT/FIM)",
            "Profondeur (VWT/NLT)": "Diepte (VWT/NLT)",
            "16x25m Speed Endurance": "16x25m Snelheid Uithouding"
        },
        "months": {
            "January": "Januari", "February": "Februari", "March": "Maart", "April": "April", "May": "Mei", "June": "Juni", 
            "July": "Juli", "August": "Augustus", "September": "September", "October": "Oktober", "November": "November", "December": "December"
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
        "club_level_performance_tab_title": "🏆 Prestaties per Niveau",
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
        "performances_overview_tab_label": "Prestatieoverzicht",
        "edit_performances_sub_tab_label": "Prestaties Bewerken",
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
        "filter_by_discipline_label": "Filter op Discipline:",
        "all_freedivers_option": "Alle Vrijduikers", 
        "all_sessions_option": "Alle Sessies",
        "all_instructors_option": "Alle Instructeurs",
        "all_disciplines_option": "Alle Disciplines",
        "filter_by_year_label": "Filter op Jaar:",
        "filter_by_month_label": "Filter op Maand:",
        "filter_by_place_label": "Filter op Plaats:",
        "all_years_option": "Alle Jaren",
        "all_months_option": "Alle Maanden",
        "all_places_option": "Alle Plaatsen",
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
        # Fallback to English if key not found in the selected language
        translation_set_en = TRANSLATIONS['en']
        value_en = translation_set_en
        try:
            for k_en in keys:
                value_en = value_en[k_en]
            if kwargs:
                return value_en.format(**kwargs)
            return value_en
        except KeyError:
            # Fallback to the key itself if not found in English either
            return key

# --- Helper for anonymization ---
def get_display_name(user_name, user_profiles, lang):
    if user_name and user_name in user_profiles:
        if user_profiles[user_name].get("anonymize_results", False):
            return _("anonymous_freediver_name", lang) 
    return user_name


# --- Data Handling for Performance Records ---
def migrate_and_clean_records(records_list, training_logs):
    """
    Ensures records have necessary fields and removes redundant ones.
    If a record is linked to a training session, `event_name` and `event_date` are removed.
    """
    updated = False
    training_log_lookup = {log['id']: log for log in training_logs}

    for record in records_list:
        if record.get('id') is None:
            record['id'] = uuid.uuid4().hex
            updated = True
        
        # Ensure entry_date exists, falling back to today's date
        if 'entry_date' not in record:
            record['entry_date'] = date.today().isoformat()
            updated = True
            
        # Ensure linked_training_session_id exists
        if 'linked_training_session_id' not in record:
            record['linked_training_session_id'] = None
            updated = True

        # If a record is properly linked, remove redundant fields
        if record.get('linked_training_session_id') in training_log_lookup:
            if 'event_name' in record:
                del record['event_name']
                updated = True
            if 'event_date' in record:
                del record['event_date']
                updated = True
            # The old 'date' field from very old versions
            if 'date' in record:
                 del record['date']
                 updated = True
    return updated

def load_records(training_logs):
    """Loads performance records and runs migration/cleaning."""
    try:
        with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        records = []
    if migrate_and_clean_records(records, training_logs): 
        save_records(records)
    return records

def save_records(records):
    """Saves performance records to the JSON file."""
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

def is_lower_better(discipline_key):
    return discipline_key in LOWER_IS_BETTER_DISCIPLINES

def parse_static_time_to_seconds(time_str, lang='en'):
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

def parse_distance_to_meters(dist_str, lang='en'):
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
    tags_colors = {
        "#apnée/marche": "#4CAF50",      # Green
        "#apnée/stretching": "#2196F3", # Blue
        "#apnée/statique": "#FFC107",    # Amber
        "#apnée/dynamique": "#f44336"    # Red
    }
    for tag, color in tags_colors.items():
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
    # The logic assumes lower is better for time-based, higher for others.
    idx = merged_df.groupby(['user', 'discipline'])['parsed_value'].idxmax()
    if discipline_keys and is_lower_better(discipline_keys[0]):
        idx = merged_df.groupby(['user', 'discipline'])['parsed_value'].idxmin()

    best_perf_df = merged_df.loc[idx]

    # Define the order and color scheme for certifications based on the provided image
    cert_order = ["NB", "A1", "A2", "A3", "S4", "I1", "I2", "I3", _("no_certification_option", lang)]
    # Colors extracted from the image and extended for other levels
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
            st.subheader(f"{_('certification_stats_header', lang)} - {_('disciplines.' + disc_key, lang)}")
            
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
                x=alt.X('certification:N', title=_("certification_level_col", lang), sort=cert_order),
                y=alt.Y('parsed_value:Q', title=y_axis_title, scale=alt.Scale(zero=False)),
                # --- Color mapping added here ---
                color=alt.Color('certification:N',
                                scale=alt.Scale(domain=cert_order, range=cert_colors),
                                legend=None  # Hide the legend as colors map directly to x-axis labels
                               ),
                tooltip=[
                    alt.Tooltip('certification', title=_("certification_level_col", lang)),
                    alt.Tooltip('formatted_perf', title=_("avg_performance_col", lang))
                ]
            ).properties(
                width=alt.Step(40)  # controls width of bars
            )
            
            # Add text labels on bars
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,  # Nudges text up so it doesn't overlap with the bar
                color='black' # Ensure text is readable
            ).encode(
                text='formatted_perf:N'
            )
            
            st.altair_chart(chart + text, use_container_width=True)


# --- Main App ---
def main():
    # Initialize session state variables
    if 'language' not in st.session_state: st.session_state.language = 'fr'
    if 'initiate_clear_training_inputs' not in st.session_state: st.session_state.initiate_clear_training_inputs = False
    if 'initiate_clear_feedback_inputs' not in st.session_state: st.session_state.initiate_clear_feedback_inputs = False
    if 'privileged_user_authenticated' not in st.session_state: st.session_state.privileged_user_authenticated = False
    if 'authenticated_privileged_user' not in st.session_state: st.session_state.authenticated_privileged_user = None
    if 'current_user' not in st.session_state: st.session_state.current_user = None 
    
    # Buffers for form resets
    if 'log_perf_input_buffer' not in st.session_state: st.session_state.log_perf_input_buffer = ""
    if 'training_place_buffer' not in st.session_state: st.session_state.training_place_buffer = "Blocry"
    if 'training_desc_buffer' not in st.session_state: st.session_state.training_desc_buffer = ""
    
    # Initialize feedback form buffers carefully
    default_lang_for_init = st.session_state.get('language', 'fr')
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

    training_log_loaded = load_training_log() 
    all_records_loaded = load_records(training_log_loaded)
    user_profiles = load_user_profiles()
    instructor_feedback_loaded = load_instructor_feedback()

    discipline_keys = ["Dynamic Bi-fins (DYN-BF)", "Static Apnea (STA)", "Dynamic No-fins (DNF)", "Depth (CWT/FIM)", "Profondeur (VWT/NLT)", "16x25m Speed Endurance"]
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
                    pass
            
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
            
    # --- Sidebar: Profile Section ---
    if current_user: 
        # Recharger le profil utilisateur à chaque changement d'utilisateur pour afficher les bons champs
        user_profile_data_sidebar = user_profiles.get(current_user, {})

        with st.sidebar.expander(_("profile_header_sidebar", lang)):
            with st.form(key="profile_form_sidebar_main", border=False): 
                # Pré-remplir les champs avec les valeurs du profil utilisateur
                current_certification_sidebar = user_profile_data_sidebar.get("certification", _("no_certification_option", lang))
                cert_level_keys_from_dict_sidebar = list(TRANSLATIONS[lang]["certification_levels"].keys())
                actual_selectbox_options_sidebar = [_("no_certification_option", lang)] + cert_level_keys_from_dict_sidebar
                try: current_cert_index_sidebar = actual_selectbox_options_sidebar.index(current_certification_sidebar)
                except ValueError: current_cert_index_sidebar = 0
                
                st.selectbox(
                    _("certification_label", lang), options=actual_selectbox_options_sidebar, 
                    index=current_cert_index_sidebar, key="certification_select_profile_form_sb" 
                )
                
                current_cert_date_str_sidebar = user_profile_data_sidebar.get("certification_date")
                current_cert_date_obj_sidebar = None
                if current_cert_date_str_sidebar:
                    try: current_cert_date_obj_sidebar = date.fromisoformat(current_cert_date_str_sidebar)
                    except ValueError: current_cert_date_obj_sidebar = None
                
                st.date_input(
                    _("certification_date_label", lang), value=current_cert_date_obj_sidebar, key="cert_date_profile_form_sb" 
                )
                
                st.text_input(
                    _("lifras_id_label", lang), value=user_profile_data_sidebar.get("lifras_id", ""), key="lifras_id_profile_form_sb" 
                )
                
                st.checkbox(
                    _("anonymize_results_label", lang), value=user_profile_data_sidebar.get("anonymize_results", False), key="anonymize_profile_form_sb" 
                )

                # Champ motivations
                st.text_area(
                    "Motivations à faire de l'apnée :", 
                    value=user_profile_data_sidebar.get("motivations", ""), 
                    key="motivations_profile_form_sb"
                )

                # Champ projection à 3 ans
                st.text_area(
                    "Où vous imaginez vous dans votre pratique de l'apnée dans 3 ans ?",
                    value=user_profile_data_sidebar.get("projection_3_ans", ""),
                    key="projection_3_ans_profile_form_sb"
                )

                # Champ texte pour le portrait photo
                st.text_area(
                    "Texte pour le portrait  photo",
                    value=user_profile_data_sidebar.get("portrait_photo_text", ""),
                    key="portrait_photo_text_profile_form_sb"
                )
                
                submitted_save_profile = st.form_submit_button(_("save_profile_button", lang))

                if submitted_save_profile:
                    user_profiles.setdefault(current_user, {}) 
                    user_profiles[current_user]["certification"] = st.session_state.certification_select_profile_form_sb
                    cert_date_val = st.session_state.cert_date_profile_form_sb
                    user_profiles[current_user]["certification_date"] = cert_date_val.isoformat() if cert_date_val else None
                    user_profiles[current_user]["lifras_id"] = st.session_state.lifras_id_profile_form_sb.strip()
                    user_profiles[current_user]["anonymize_results"] = st.session_state.anonymize_profile_form_sb
                    user_profiles[current_user]["motivations"] = st.session_state.motivations_profile_form_sb.strip()
                    user_profiles[current_user]["projection_3_ans"] = st.session_state.projection_3_ans_profile_form_sb.strip()
                    user_profiles[current_user]["portrait_photo_text"] = st.session_state.portrait_photo_text_profile_form_sb.strip()
                    save_user_profiles(user_profiles)
                    st.success(_("profile_saved_success", lang, user=current_user))
                    st.rerun()

    # --- Sidebar: Logging Forms (Reordered) ---
    if is_sidebar_instructor_section_visible:
        st.sidebar.header(_("log_training_header_sidebar", lang))
        with st.sidebar.form(key="log_training_form_sidebar"):
            st.date_input(_("training_date_label", lang), date.today(), key="training_date_form_key")
            st.text_input(_("training_place_label", lang), value=st.session_state.training_place_buffer, key="training_place_form_key")
            st.text_area(_("training_description_label", lang), value=st.session_state.training_desc_buffer, key="training_desc_form_key")
            
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
                    st.session_state.initiate_clear_training_inputs = True
                    st.rerun()

    st.sidebar.header(_("log_performance_header", lang))
    if not current_user:
        st.sidebar.warning(_("select_user_first_warning", lang))
    else:
        with st.sidebar.form(key="log_performance_form_sidebar_main"): 
            st.write(_("logging_for", lang, user=current_user))

            if not training_log_loaded:
                st.warning("Veuillez d'abord créer une session d'entraînement.")
                st.form_submit_button(_("save_performance_button", lang), disabled=True)
            else:
                training_session_options = {ts.get('id'): f"{ts.get('date')} - {ts.get('place', 'N/A')}" for ts in sorted(training_log_loaded, key=lambda x: x.get('date', '1900-01-01'), reverse=True)}
                
                selected_training_session_id = st.selectbox(
                    _("link_training_session_label", lang),
                    options=list(training_session_options.keys()),
                    format_func=lambda x: training_session_options[x],
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
                elif log_discipline_original_key_perf_form in ["Dynamic Bi-fins (DYN-BF)", "Dynamic No-fins (DNF)", "Depth (CWT/FIM)", "Profondeur (VWT/NLT)"]:
                    performance_help_text_perf_form = _("dyn_depth_help", lang)

                st.text_input(
                    _("performance_value", lang), 
                    value=st.session_state.log_perf_input_buffer, 
                    help=performance_help_text_perf_form, 
                    key="log_perf_input_form_widget_key"
                )

                submitted_save_perf = st.form_submit_button(_("save_performance_button", lang))

                if submitted_save_perf:
                    current_log_perf_str = st.session_state.log_perf_input_form_widget_key.strip()
                    if not current_log_perf_str: 
                        st.error(_("performance_value_empty_error", lang))
                    else:
                        parsed_value_for_storage = None
                        if is_time_based_discipline(log_discipline_original_key_perf_form):
                            parsed_value_for_storage = parse_static_time_to_seconds(current_log_perf_str, lang)
                        else:
                            parsed_value_for_storage = parse_distance_to_meters(current_log_perf_str, lang)
                        
                        if parsed_value_for_storage is not None:
                            new_record = {
                                "id": uuid.uuid4().hex, 
                                "user": current_user,
                                "entry_date": date.today().isoformat(), 
                                "discipline": log_discipline_original_key_perf_form,
                                "original_performance_str": current_log_perf_str, 
                                "parsed_value": parsed_value_for_storage,
                                "linked_training_session_id": selected_training_session_id
                            }
                            all_records_loaded.append(new_record)
                            save_records(all_records_loaded)
                            st.success(_("performance_saved_success", lang, user=current_user))
                            st.session_state.log_perf_input_buffer = "" 
                            st.rerun()

    if is_sidebar_instructor_section_visible:
        st.sidebar.header(_("log_feedback_header_sidebar", lang))
        with st.sidebar.form(key="log_feedback_form_sidebar"): 
            if not all_known_users_list: st.warning("Please add freedivers before logging feedback.") 
            else:
                freediver_options_for_feedback = [_("select_freediver_prompt", lang)] + all_known_users_list
                
                default_fb_user_idx = 0
                try:
                    default_fb_user_idx = freediver_options_for_feedback.index(st.session_state.feedback_for_user_buffer)
                except (ValueError, KeyError):
                    st.session_state.feedback_for_user_buffer = _("select_freediver_prompt", lang)

                st.selectbox(
                    _("feedback_for_freediver_label", lang), 
                    options=freediver_options_for_feedback, 
                    index=default_fb_user_idx,
                    key="feedback_for_user_selectbox_key_in_form"
                )
                
                training_session_options_fb_form = {log['id']: f"{log.get('date', '')} - {log.get('place', '')}" for log in sorted(training_log_loaded, key=lambda x: x.get('date', '1900-01-01'), reverse=True)}
                training_session_options_display_fb_form = [_("select_training_prompt", lang)] + list(training_session_options_fb_form.values())
                
                default_fb_ts_idx = 0
                try:
                    default_fb_ts_idx = training_session_options_display_fb_form.index(st.session_state.feedback_training_session_buffer)
                except (ValueError, KeyError):
                    st.session_state.feedback_training_session_buffer = _("select_training_prompt", lang)

                st.selectbox(
                    _("training_session_label", lang), 
                    options=training_session_options_display_fb_form, 
                    index=default_fb_ts_idx,
                    key="feedback_training_session_selectbox_key_in_form"
                )
                
                st.write(f"{_('instructor_name_label', lang)} {current_user}") 
                
                st.text_area(
                    _("feedback_text_label", lang), 
                    value=st.session_state.feedback_text_buffer, 
                    key="feedback_text_area_key_in_form" 
                )

                submitted_save_feedback = st.form_submit_button(_("save_feedback_button", lang))

                if submitted_save_feedback:
                    sel_fb_for_user = st.session_state["feedback_for_user_selectbox_key_in_form"]
                    sel_fb_training_disp = st.session_state["feedback_training_session_selectbox_key_in_form"]
                    sel_fb_text = st.session_state["feedback_text_area_key_in_form"].strip() 
                    
                    sel_fb_training_id = None
                    if sel_fb_training_disp != _("select_training_prompt", lang):
                        for log_id, display_str in training_session_options_fb_form.items():
                            if display_str == sel_fb_training_disp:
                                sel_fb_training_id = log_id
                                break
                    
                    if sel_fb_for_user == _("select_freediver_prompt", lang): st.error("Please select a freediver for the feedback.") 
                    elif not current_user: st.error("Instructor not identified.") 
                    elif not sel_fb_text: st.error(_("feedback_text_empty_error", lang))
                    else:
                        new_feedback = {
                            "id": uuid.uuid4().hex,
                            "feedback_date": date.today().isoformat(),
                            "diver_name": sel_fb_for_user,
                            "training_session_id": sel_fb_training_id,  # <-- Correction ici
                            "instructor_name": current_user,
                            "feedback_text": sel_fb_text
                        }
                        instructor_feedback_loaded.append(new_feedback)
                        save_instructor_feedback(instructor_feedback_loaded)
                        st.success(_("feedback_saved_success", lang))
                        st.session_state.initiate_clear_feedback_inputs = True
                        st.rerun()
                        
    # --- Sidebar: Language Selector (Moved to bottom) ---
    st.sidebar.markdown("") 
    language_options = {"English": "en", "Français": "fr", "Nederlands": "nl"}
    current_lang_display_name = [k_disp for k_disp, v_code in language_options.items() if v_code == lang][0]
    
    selected_lang_display_name = st.sidebar.selectbox(
        _("language_select_label", lang), options=list(language_options.keys()),
        index=list(language_options.keys()).index(current_lang_display_name),
        key="language_selector_widget"
    )
    new_lang_code = language_options[selected_lang_display_name]
    if st.session_state.language != new_lang_code:
        st.session_state.language = new_lang_code
        st.rerun()
    lang = st.session_state.language

    # --- Main Display Area ---
    tab_label_personal = _("personal_records_tab_label", lang)
    tab_label_feedback = _("my_feedback_tab_label", lang)
    tab_label_level_performances = _("club_level_performance_tab_title", lang)
    tab_label_club_performances = _("club_performances_overview_tab_label", lang)
    tab_label_freedivers = _("freedivers_tab_title", lang) 
    tab_label_main_training_log = _("training_log_tab_title", lang)
    tab_label_performance_log = _("performance_log_tab_label", lang)
    tab_label_main_feedback_log = _("feedback_log_tab_label", lang)

    if not current_user:
        st.info(_("select_user_prompt", lang))
    else:
        # Define tabs for all users
        tabs_to_display_names_main = [tab_label_personal, tab_label_feedback, tab_label_level_performances]
        
        # Define tabs for admin users
        admin_tabs = []
        if is_admin_view_authorized:
            admin_tabs = [
                tab_label_club_performances,
                tab_label_freedivers, 
                tab_label_main_training_log, 
                tab_label_performance_log, 
                tab_label_main_feedback_log
            ]
        
        tabs_to_display_names_main.extend(admin_tabs)
        tab_objects_main = st.tabs(tabs_to_display_names_main)
        
        # Tab 1: My Performances
        with tab_objects_main[0]:
            user_records_for_tab = [r for r in all_records_loaded if r['user'] == current_user]
            if not user_records_for_tab:
                st.info(_("no_performances_yet", lang))
            else:
                with st.container(border=True):
                    st.subheader(_("personal_bests_subheader", lang))
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
                            translated_full_discipline_name_tab = _("disciplines." + disc_key_pb_col_tab, lang)
                            short_disc_name_tab = translated_full_discipline_name_tab.split('(')[0].strip()
                            st.metric(label=_("pb_label", lang, discipline_short_name=short_disc_name_tab), value=val_tab)
                            if event_date_tab: 
                                st.caption(_("achieved_on_event_caption", lang, event_name=event_name_tab, event_date=event_date_tab))
                            elif val_tab == "N/A": 
                                st.caption(_("no_record_yet_caption", lang))
                
                st.markdown("")
                
                sub_tab_titles_user = [_("disciplines." + key, lang) for key in discipline_keys]
                sub_tabs_user = st.tabs(sub_tab_titles_user)

                for i_sub_tab_user, disc_key_sub_tab_user in enumerate(discipline_keys):
                    with sub_tabs_user[i_sub_tab_user]:
                        # Chart Data
                        chart_data_list = []
                        for r_chart in sorted(user_records_for_tab, key=lambda x: get_training_session_details(x.get('linked_training_session_id'), training_log_loaded).get('event_date') or '1900-01-01'):
                            if r_chart['discipline'] == disc_key_sub_tab_user and r_chart.get('parsed_value') is not None:
                                session_details = get_training_session_details(r_chart.get('linked_training_session_id'), training_log_loaded)
                                if session_details.get('event_date'):
                                    chart_data_list.append({
                                        "Event Date": pd.to_datetime(session_details['event_date']), 
                                        "PerformanceValue": r_chart['parsed_value'],
                                        "Event Name": session_details['event_name']
                                    })
                        
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
                        
                        # History Table
                        st.markdown(f"#### {_('history_table_subheader', lang)}")
                        history_for_editor_raw = [r for r in user_records_for_tab if r['discipline'] == disc_key_sub_tab_user]
                        if not history_for_editor_raw:
                            st.caption(_("no_history_display", lang))
                        else:
                            training_session_options = {ts.get('id'): f"{ts.get('date')} - {ts.get('place', 'N/A')}" for ts in sorted(training_log_loaded, key=lambda x: x.get('date', '1900-01-01'), reverse=True)}
                            session_display_to_id = {v: k for k, v in training_session_options.items()}
                            
                            history_for_editor_display = []
                            for rec in sorted(history_for_editor_raw, key=lambda x: get_training_session_details(x.get('linked_training_session_id'), training_log_loaded).get('event_date') or '1900-01-01', reverse=True):
                                session_display = training_session_options.get(rec.get("linked_training_session_id"), "N/A")
                                history_for_editor_display.append({
                                    "id": rec.get("id"),
                                    _("link_training_session_label", lang): session_display,
                                    _("history_performance_col", lang): rec.get("original_performance_str", ""),
                                    _("history_delete_col_editor", lang): False
                                })
                            
                            edited_df = st.data_editor(
                                pd.DataFrame(history_for_editor_display),
                                column_config={
                                    "id": None,
                                    _("link_training_session_label", lang): st.column_config.SelectboxColumn(options=list(training_session_options.values()), required=True),
                                    _("history_performance_col", lang): st.column_config.TextColumn(label=_("history_performance_col", lang), required=True),
                                    _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(label=_("history_delete_col_editor", lang))
                                },
                                hide_index=True, key=f"data_editor_{current_user}_{disc_key_sub_tab_user}"
                            )

                            if st.button(_("save_history_changes_button", lang), key=f"save_hist_{disc_key_sub_tab_user}"):
                                changes_made = False
                                records_to_process = [r for r in all_records_loaded if not(r['user'] == current_user and r['discipline'] == disc_key_sub_tab_user)]
                                
                                for row in edited_df.to_dict('records'):
                                    if row[_("history_delete_col_editor", lang)]:
                                        changes_made = True
                                        continue

                                    original_rec = next((r for r in history_for_editor_raw if r['id'] == row['id']), None)
                                    if not original_rec: continue

                                    new_perf_str = str(row[_("history_performance_col", lang)]).strip()
                                    new_session_id = session_display_to_id.get(row[_("link_training_session_label", lang)])

                                    if original_rec.get('original_performance_str') != new_perf_str or original_rec.get('linked_training_session_id') != new_session_id:
                                        changes_made = True
                                        parsed_val = parse_static_time_to_seconds(new_perf_str, lang) if is_time_based_discipline(disc_key_sub_tab_user) else parse_distance_to_meters(new_perf_str, lang)
                                        if parsed_val is not None:
                                            original_rec['original_performance_str'] = new_perf_str
                                            original_rec['parsed_value'] = parsed_val
                                            original_rec['linked_training_session_id'] = new_session_id
                                        else:
                                            st.error(f"Invalid performance format for '{new_perf_str}'")
                                    
                                    records_to_process.append(original_rec)


                                if changes_made:
                                    save_records(records_to_process)
                                    st.success(_("history_updated_success", lang))
                                    st.rerun()
                                else:
                                    st.info("No changes detected.")

        # Tab 2: My Feedback
        with tab_objects_main[1]: # My Feedback
            st.subheader(_("my_feedback_tab_label", lang))
            user_feedback = [fb for fb in instructor_feedback_loaded if fb.get('diver_name') == current_user]
            
            if not user_feedback:
                st.info(_("no_feedback_to_summarize", lang))
            else:
                if st.button(_("generate_feedback_summary_button", lang)):
                    with st.spinner("Génération du résumé..."):
                        all_feedback_text = "\n".join([f"- {fb['feedback_text']}" for fb in user_feedback])

                        adeps_coaching_instructions = '''
                        
                        À partir de maintenant, et pour toute notre conversation, tu vas agir en tant que moniteur sportif initiateur formé par l'Adeps. Ton rôle et tes réponses doivent être scrupuleusement basés sur la philosophie, la méthodologie et les principes décrits dans le document de formation "Didactique et méthodologie - Module 2 : Ma séance/mon intervention".

                        Voici les instructions précises que tu dois suivre pour incarner ce rôle :

                        1. Mission principale :
                        Tes objectifs généraux sont toujours : Animer, Initier, et Fidéliser. Ton but ultime est de faire découvrir une discipline dans un climat positif pour encourager une pratique du sport à long terme.
                        2. Style d'intervention :
                        Tu adopteras systématiquement un style coopératif ("l'enseignant").
                        Tu partages la prise de décision avec les sportifs.
                        Tu les guides pour qu'ils deviennent autonomes et responsables.
                        Tu n'es ni un "dictateur" (style directif) qui impose tout, ni un "baby-sitter" (style laisser-faire) qui est passif.
                        3. Conception des séances et des tâches :
                        Les "4 AS" : Chaque activité ou conseil que tu donnes doit viser à intégrer les "4 AS" : Apprentissage, Activation, Amusement, et Attitudes.
                        La "Délicieuse Incertitude" : Tu dois concevoir ou adapter les exercices pour que le sportif se situe dans sa "zone de difficulté optimale", c'est-à-dire avec un taux de réussite de 70 à 80%. Le but est que la tâche ne soit ni trop facile (ennui) ni trop difficile (anxiété, découragement).
                        Structure de séance : Toute séance que tu décris ou proposes doit respecter la structure en trois parties :
                        Partie préparatoire (échauffement).
                        Partie fondamentale (corps de la séance).
                        Partie finale (retour au calme et débriefing).
                        Adaptabilité : Tu dois être capable de simplifier ou de complexifier une tâche pour l'adapter au niveau du pratiquant.
                        4. Communication et Feedback :
                        Clarté : Ton langage doit être simple et tes phrases courtes. "Ce qui s'énonce simplement se comprend facilement".
                        Feedback constructif : Lorsque tu donnes un feedback, tu dois :
                        Prioriser le renforcement positif. Le rapport doit être d'environ 3 à 4 réactions positives pour 1 négative.
                        Être spécifique et non général. Explique pourquoi une action était bonne.
                        Corriger l'erreur primaire, pas seulement ses conséquences.
                        Ne pas donner d'informations redondantes (par exemple, dire qu'une balle est dans le filet si le joueur le voit déjà).
                        Questionnement : Utilise des questions ouvertes pour stimuler la réflexion du sportif sur sa propre pratique.
                        5. Gestion de groupe et attitude :
                        Tu dois toujours chercher à instaurer et maintenir un climat positif et bienveillant.
                        Ton rôle est d'être un animateur : tu vis la séance avec les participants, tu encourages, tu relances l'activité et tu motives.
                        Pour la gestion des problèmes, tu privilégies la prévention en créant un environnement de travail positif et en valorisant les bons comportements.
                        En résumé, tu es un coach pédagogue, structuré, motivant et bienveillant. Chacune de tes réponses doit refléter cette approche et s'appuyer sur les concepts du document fourni.
                        
                        '''

                        huron_spirit = '''

                        - tous les moniteurs ont tjrs raison selon eux... Le sport évolue beaucoup. Rester ouvert. Fonctionnement par chapitre, on travaille les chapitres un par un, et tant que c'est pas passé, on travaille le chapitre en question. Sur le moment on ne demande jamais pourquoi on nous donne une instruction, mais on peut en discuter une fois sorti de l'eau. On donne ce qui est nécessaire comme explication avant l'exercice si nécessaire.
                        - longe si on ne voit rien (sans masque, myope, mauvaise visi) ou si descend au delà de 30m.
                        - pas de rendez-vous syncopal des 7m. Prouvé que ça n'existe pas. Beaucoup de syncopes au départ ces dernières années. L'histoire des pressions partielles n'existe pas.
                        - les muscles ne fonctionnent que dans un sens. Il a un tjrs un muscle pour un sens, et un autre pour l'autre sens.
                        - on travaille d'abord la décontraction : vérifier les crispations naturelles et qu'on est droit. Ça va nous permettre d'être détendu et donc de pouvoir aller chercher de l'air dans les poumons car le diaphragme peut bouger.
                        - on peut se ventiler au tuba, l'espace mort fait quelques centilitres, rien par rapport à notre volume inspiré avant la Descente 4-5 l, ou même 1.5-2 l Durant la ventilation. Cette règle vient de la nage avec palmes.
                        - Poser son pied à plat sur la table et l'incliner vers l'avant. Certains nageurs savent toucher avec les orteils sur la table. La majorité non, et à besoin d'une inclinaison de la palme, pour avoir un bon plié avant et arrière. En piscine, c'est différent, car il ne faut pas que la palme remonte en surface, on est plus sur 2/3 bas 1/3 descente. 
                        - exercice pour moi : d'abord à la corde, puis statique à 10 m pour checker le lestage, puis freefall et on palme juste après, puis Michael Jackson doigt anus..., puis on continue. Ma palme cressi a un noyau dur. Pas adapté. Va me donner des autres palmes.

                        - séance hypoxie, plus en relâchement 
                        - pas de situation où on est 100% détendu, on tend vers ça, mais pas être perfectionniste
                        - personne n'a aucun échecs, apprendre a gérer les échecs
                        - concentration / attention : ramener l'attention sur quelque chose de choisi.  Ça nécessite aussi de l'entraînement.
                        - important de rester dans l'observation 
                        - peur : qu'une peur soit vraie ou pas, important de déterminer si cette peur est utile pour moi là maintenant 
                        - État de flow : état où on est vmt dans le moment présent. On ne recherche pas l'état de floW. Il arrive quand on s'y attend pas. On est pas dans l'après. On est dans l'instant présent. On peut se concentrer sur certaines choses pour ramener notre attention dans l'instant présent.
                        - "anapana" important pour se recentrer, ressentir les micro-sensations. On peut même le faire à la bouée avec le masque. Se concentrer sur la zone entre la base du nez et la lèvre supérieure. 
                        - mot choisi : "confiance"
                        - phrase choisie : "je peux le faire"
                        - grosse discussion sur les peurs, les peurs indirectes comme la famille, etc. En gros, l'apnée c'est une méditation sous l'eau. On va voir les repères qui nous permettent de dire s'il y a un risque syncopal. La syncope hypoxique n'arrive que pour les champions, et ça se travaille. Pour les autres, une syncope (malaise) peut arriver plus tôt dû à des facteurs parasites. Il faut à tout prix éviter la génération d'adrénaline, qui arrive quand on est pris dans un train de pensées. Même ceux qui descendent profonds peuvent avoir des plongées compliquées mentalement, d'où l'idée d'arriver à se recentrer. 
                        - sans sortir de sa zone de confort, on ne grandit pas. Allons-y petit à petit 
                        - très peu d'accidents en apnée. 

                        - Il n'y a aucun accident en apnée encadrée, à part un, un jour, qui a fait un squeeze, et à quand même replongé le lendemain, a craché du sang et c'est noyé dedans.
                        - plusieurs morts en apnée libre par contre. Mais c'était pas encadré, peu organisé, lié à des erreurs, ... 
                        - discussion sur la sécurité, important de donner confiance aux gens, on peut accompagner au début, mais rapidement mettre en confiance. Au final, il ne faut pas projeter nos anxiétés sur l'autre. Pas nécessaire de mettre des sécurités pour des problèmes inexistants (longe, sécu à 5-10 m, accompagner l'apnéiste à chaque descente, rester en permanence à côté, etc) NDLR : comme la parentalité :)
                        - important de mettre un cadre, et de mettre des règles strictes par contre, sur le fait de rester dans sa zone de confort. 
                        - important de rester droit, pour décontracter les muscles, surtout que tout diminue en volume avec la pression. 
                        - échauffement : statique à 10 m, puis descente en FIM et on palme après le FIM pour être certain qu'on élimine le risque de 'spoiler' (aileron, qui nous ferait dévier de notre trajectoire)

                        - avant 100 m en dyn et 4 min d'apnée, c'est essentiellement les spasmes qu'il faut travailler. La vasoconstriction, les grésillements dans les jambes, etc. n'arrivent qu'après.
                        - exercice sur le diaphragme, on rentre son diaphragme. Est-ce que c'est les abdos, non. On fait pareil mais on mime l'ouverture de la poitrine : le diaphragme remonte. Pareil mais on serre les fesses : on voit que serrer les abdos fait redescendre le diaphragme. 
                        - au niveau du ressenti des contractions, certaines personnes ne ressentent en effet pas les contractions. Mais ils en ont quand même. On peut leur faire ressentir en mettant notre main sur leur ventre.
                        - en tant qu'instructeur, c'est important de pouvoir hyperventiler pour repartir rapidement sous l'eau. Mais rester bien en delà de sa limite d'apnée. 
                        - au niveau des syncopes (perte de conscience), seulement 10% dont des syncopes hypoxiques. Les autres sont des pertes de connaissances autres (malaise vagal, ...)
                        - l'ensemble de l'air dans l'oreille va subir la pression ambiante car elle baigne dans de l'air, qui qui change de volume, et donc qui aspire le tympan vers l'intérieur.
                        - exercice à la corde pour le FIM : important de tirer avec les muscles du dos pour ne pas tendre les abdos. Il faut donc attraper la corde en l'entourant et en plaçant la main devant soi. Ensuite on tire et on attend bien que la première main soit en bas avant d'envoyer l'autre main, et on profite bien de la glisse. On peut même faire une rotation et regarder sur le côté quand on tire pour être certain d'utiliseres muscles du dos (comme sur les vidéos de compet).
                        - 7-8 m tête en bas, 15-20 m tête en haut
                        - Frenzel min 50m, voir plus, en fonction de la souplesse de la cage thoracique 
                        - exercices a gonfler ses voiles de nez avec les doigts sous le nez, puis on fait des fuites d'air. On ne fait pas forcément Frenzel si on compense bouche ouverte (à rediscuter).
                        - 3 raisons pour lesquelles un Frenzel ne marche pas : pas détendu, pousser par le ventre, pas droit (donc être droit, être relax et gèrer le masque)
                        - après le freefall environ (àpd 15m), ou apd 28m pour Pascal (il est déjà en chute libre mais c'est sa dernière charge), on pince le nez et on ne le lâche plus. Ça permet d'éviter que l'air du masque ne soit pas aspiré et avec l'effet de suction que le voile du palais remonte et qu'on ne puisse plus compenser et descendre plus bas. 
                        - au niveau de la compensation, pas moyen de contrôler directement la glotte et le voile du palais, ils sont contrôlés pas l'envie d'inspirer ou expirer.
                        - pour sentir le voile du palais, on inspire pr le nez puis on expire par la bouche, et inversement.
                        - pour sentir sa glotte, on lâche de l'air par à-coups bouche ouverte.
                        - explication pelizarri démontée : on peut tjrs prendre de l'air dans les poumons en frenzel. On ne stocke pas de l'air dans la bouche avec une charge pour du Frenzel. Car on ne saurait pas l'utiliser sans mouvement de langue. De la même manière, l'ottovent ne sert à rien (à part pour entraîner son mouthfill)
                        - BTV : n'existe qu'en français. En anglais c'est hands-free. L'idée c'est que l'on peut pas gérer ses trompes d'Eustache volontairement. Par contre, un nombre très réduit d'apnéistes a des facilités. Comme pelizarri, nox, ...

                        - Étude de 2006-2007 qui démontre que la baisse d'oxygène est inexistante chez des apnéistes de l'équipe de France. Trouver la publication. 
                        - motivation : discipline où il y a encore des changements et des nouvelles découvertes, et l'âge n'a pas d'importance, on ne se sent pas vieillir :)
                        - nouvelle explication avec l'analogie du soufflet pour le Frenzel. On démonte le fait qu'il faille bloquer la glotte pour faire du Frenzel. En fait on l'ouvre automatiquement à chaque fois qu'on compense en allant chercher de l'air dans les poumons.
                        - l'apnée est un sport, donc une discipline où l'on cherche constamment à se mesurer par rapport à soi-même. Contrairement à d'autres sport, on est en en compétition avec soi même uniquement.
                        - impossible de tout contrôler, donc on se fixe des jalons, des choses que l'on aimerait qui se passent bien. La différence entre un athlète loisir et et un athlète pro, c'est le perfectionnisme. Le perfectionnisme ça tue la vie. Ça fait qu'on est tjrs insatisfait. Rien n'est parfait. Progresser, s'ameliorer c'est bien. Viser à être parfait c'est pas bien. Un athlète pro sait que sans bien faire, il y arrive quand même. 
                        - on va fixer une longueur de corde. Ne pas se concentrer sur l'objectif. Se concentrer sur les gestes à travailler. On évite l'auto sabotage, qui peut même être inconscient.
                        - Guy boux. Champion mais fait essentiellement du sauna comme entraînement... Donc en gros, c'est important qu'on soit essentiellement relax.
                        - échauffement : c'est un véritable effort dans les autres sports. En apnée, on fait des apnées faciles mais qui sont très rapidement inconfortables. On en fait généralement trois, et on voit qu'elles sont de moins en moins inconfortables.
                        - circulation sanguine avec débit qui diminue avec la vasoconstriction, battements du cœur qui diminuent, ... lors d'un no warmup. On profite du réflexe d'immersion. Mais ! ... C'est accompagné de tout un tas de sensations. On doit donc gérer tout un tas de sensations liées au fait que le corps est en train de faire tout ce qui faut pour rester en vie, que c'est gravé en nous quelque part dans notre ADN. On note que les réflexes d'immersion reviennent après plusieurs apnées, mais genre 1h plus tard. Donc, dans les faits, on note une différence de 10 BPM entre la première apnée avec réflexes d'immersion et la troisième. Mais après une heure, on tombe à niveau aux BPM de la première apnée. En compet', certains font du bon warmup, et d'autres font des grosses apnées, genre 4min poumons vides, pour raccourcir la période d'une heure, et être avec un bon BPM lors de la perf. Par contre, on est plus relax si on en fait plusieurs. Donc, il faut trouver ce que nous convient le plus. Pour être certain d'avoir une bonne echauf, il faut accepter les sensations que l'on va sentir pendant l'échauffement, c'est désagréable, mais c'est ok. Plus on accepte ses sensations pendant les premières échauff, plus on va évoluer.
                        - discussion sur différences entre production de l'adrénaline souvent associée à la peur, et les sensations. Les sensations sont associées à la production d'un tas d'autres hormones. C'est normal de rechercher des sensations, mais il faut tout de même limiter ses peurs (?). Il faut des peurs, car c'est ça qui nous retient à la vie. Mais c'est important des les apprivoiser. 

                        - quand on a eu une grosse peur, on est sous l'effet d'hormones qui nous disent : réagis, et alors le cerveau se met naturellement en mode automatique. Cela nous empêche de faire les choses de manières raisonnée. C'est important de rester en mode contrôle. Il ne faut pas accuser l'oreille de tous les maux, il faut chercher les clés de la compensation ailleurs. On peut avoir de manière ponctuelle une présence de mucus qui nous empêche de compenser. Mais c'est souvent aussi des problèmes de ventre, d'être droit, etc.
                        - La peur de la réussite est plus fréquente et insidieuse que la peur de ne pas y arriver, car elle présente plus de conséquences. La peur de réussir, est associée au syndrome du second, un syndrome qui fait qu'on s'autosabote pour ne pas porter le poids de la réussite et du statut et conséquences sociales qui en découlent. 
                        - un contrôlant ne se confond pas avec un perfectionniste. On nous incite depuis petit à être perfectionniste, à réussir, à faire les choses bien, à être un bon élève, un bon enfant, un bon citoyen, etc. Un perfectionniste cherche à maîtriser les circonstances.
                        - le pire qui peut nous arriver c'est une syncope, mais les conséquences sont nulles. A part pour l'ego, ou la relation aux copains, etc. Pour le reste, on récupère très bien. Il y a aucun impact.
                        - "La confiance en soi" ne se construit pas du jour au lendemain. Elle se construit par les conséquences de nos actions. Si on coache quelqu'un, il faut faire en sorte de créer des environnements dans lesquels la personne puisse réussir. 
                        - attention avec trop de sécurité, car ça instaure une notion de danger, et le fait de surprotéger d'autonomise par la personne et ne lui donne pas confiance en elle.

                        - pour juger l'étape d'après, on juge l'étape d'hier. 1) est-ce que j'ai atteint la profondeur ? Non. Je change rien. J'ai eu mal à l'oreille. Non. C'était pas facile mais ok point de vue compensation. Alors oui, je sors de ma zone de confort. Est-ce que je suis remonté en mode panique. Si ça allait à peu près, alors oui je sors de la zone de confort. Est-ce que quand tu étais en surface tu t'es dit c'est chaud mais tu as déjà connu pire dans ta vie comme effort. Alors oui, je peux augmenter. Est-ce que j'ai respecté la consigne qu'on m'a donné hier. Si non, alors non. 
                        - "armure de l'apnée", le corps se transforme pour se mettre en mode apnée, il fait plein de mécanismes qu'on peut pas vraiment contrôler, mais qui nous aident. Il faut donc accepter que l'on est dans de bonnes dispositions. 
                        - conseil de Pascal pour la remontée, faire un bodys

                        2 causes les plus fréquentes de syncopes : 1) pas de ventilation suffisante après l'apnée et à cause de la vasoconstriction, le cerveau n'est plus suffisamment irrigué et donc on fait une hypoxie cérébrale. 2) malaise vagal. Le nerf vague est comprimé et on perd connaissance. On fait une démo à sec, je me remplis les poumons à fond. Et Pascal appuie fortement sur le bas ventre pendant quelques secondes, et je tombe dans les vapes. Confirmation de Vincent. J'ai voté perdu connaissance quelques secondes.

                        - Ne pas se laisser emporter pas ses émotions. Garder le contrôle, et rester concentré sur les consignes, la technique. On peut faire l'anapana pour se recentrer. Le cerveau nous donne énormément d'informations à la seconde, l'apnée nous donne l'occasion de pouvoir de recentrer, se refocaliser.
                        - On peut se surcharger en oxygène. Pas le sang, mais ailleurs dans le corps. Hyperventiler permet de diminuer la concentration de CO2, on est plus confort, moins de spasme, mais on enclenche pas les mécanismes d'économie d'énergie. Donc il faut bien se connaître et rester dans des apnées peu engagées (ça dépend de chacun, Pascal, 70 m c'est pas engagé). 
                        - Pour la dernière inspiration, c'est pas nécessaire de prendre une longue inspi avec claviculaire et tout le bazar, ça sert a rien. L'important c'est de se sentir bien, ou alors bien se remplir, mais prendre quelques secondes pour se relaxer avant de partir. Le plus efficace, c'est la carpe, parce que c'est la seule manière de remplir plus ses poumons, jusqu'à 3l. Bien remplir le bas ventre, ne pas lever les épaules pour remplir le haut. Ce qui est important c'est de remplir bas, sur le côté, et derrière.
                        - Avec la vasoconstriction, le corps retire le sang des organes inutiles, pour le rediriger vers les organes nobles. Pour se faire, le corps prends le sang là où il y en a le plus, dans les cuisses. D'où l'impression de cuisses qui chauffent. Picotement dans les doigts ? Pareil, manque de sang. 
                        - Tous ces signes que l'on appelait signes présyncopaux, sont en fait des signes que l'on fait des apnées engagées. C'est normal, c'est de l'apnée. Et l'apnée, c'est savoir gérer ses sensations.
                        - On s'est demandé si ce ne sont pas des syncopes hypoxiques, alors qu'est-ce c'est. Par exemple une des plus fréquentes, est le malaise vagal. Ça arrive par exemple sur les syncopes de départs. Ça ne peut pas être hypoxique. Donc il y a probablement d'autres causes. Le nerf vague. Qui traverse la colonne vertébrale. Et se trouve entre la colonne vertébrale, et les poumons. Dès que l'on a les poumons pleins, et qu'on a des spasmes étant tendus, on risque de se pincer le nerf vague. Important donc de ne pas associer syncope et limite hypoxique. Le champion branco petrovic carpe pendant 1min30 125 carpes... donc les signes de syncopes c'est le côté tendu qui lutte. Si qqun est dans le plaisir, pas de souci. Si quelqu'un est dans le dur, il faut intervenir. Il est pas détendu et risque le malaise vagal.
                        - Si on est dans la lutte, c'est pas bon. On va pas à chaque fois aller plus profond en tirant un peu plus sur la corde à chaque fois. On va plutôt travailler sur la détente, les différents gestes techniques, pour augmenter progressivement sa profondeur, en se sentant bien à chaque palier. 
                        - Malaise vagal > lié à la tension. Si quelqu'un est tendu, on ne le fait pas progresser. Ce n'est pas avec la capacité de tenir la résistance, qu'on va progresser.
                        - Deuxième cause la plus fréquente de syncope. L'hypoxie cérébrale, où syncope hypoxique cérébrale. S'il y a des peurs, du stress, ... On libère de l'adrénaline. Cette adrénaline va faire augmenter le rythme cardiaque, et amener le sang vers les muscles de fuites, donc pas le cerveau. Du coup, syncope hypoxique cérébrale. 
                        - Pour un débutant, préférer un sur lestage, pour qu'il ne galére pas trop à descendre. Par après, si on veut travailler la technique, alors on sous leste. Au début, on cherche l'équilibre à 10 m en étant bien rempli en surface.
                        - Quand on commence vers les 40-50m, alors on commence à attaquer les apnées hypoxiques. C'est donc important  de bien se ventiler à la sortie. Il ne faut pas trop expirer, on chie son CO2, ça fait du bien... Mais bien inspirer, rapidement. On met de l'air, on met de l'air. Il faut bien 4-5 inspirations avant que l'apnée soit considérée comme terminée. On attrape quand même bien la bouée à la sortie. 

                        - La présence de CO2 va changer l'acidité du sang, et va enclencher tout un tas de phénomènes. L'augmentation du cycle respiratoire est une conséquence d'une augmentation de l'effort. Et on a besoin d'évacuer le CO2. L'élimination du CO2 est un réflexe expiratoire. Deux zones avec lesquelles on peut jouer. Poitrine et ventre. Il faut absolument desserrer les muscles expiratoires pour mieux vivre les spasmes. Valable aussi en statique et en dynamique.
                        - Exercice : serrer le périnée et desserrer l'anus. Pas possible. Serrer la nuque et desserrer les épaules. Pas possible. 
                        - On commence d'abord à faire plein de longueurs où on est bien. Puis on passe à la gestion des spasmes. Puis à l'entraînement physique.
                        - Exercice : on travaille sur le premier spasme. Et on malaxe le ventre pour faciliter la gestion des prochains spasmes. Pours s'entraîner, faire un auto-massage du bas ventre, et s'entrainer à être relax et sortir au premier spasme. Faire ça régulièrement pour imprimer cette habitude. 

                        '''
                        
                        prompt = f"Voici une série de feedbacks pour un apnéiste. Tu es un coach d'apnée bienveillant tel que décrit ici \n{adeps_coaching_instructions}. Tu dois fournir un paragraphe encourageant, qui peux faire référence à des feedbacks précis, mais exprimés de manière confortante. Tu peux consulter des sites de références sur le web ainsi que des méthodes sur le coaching et la communication non violente. Voici de la théorie d'un coach que tu peux utiliser pour ton feedback: {huron_spirit}. Ne mentionne pas d'évènement spécifique qui pourrait être traumatisant. Le niveau actual de l'apnéiste est le suivant : {current_cert_index_sidebar}. Feedbacks:\n{all_feedback_text}"
                        
                        try:
                            # This is a placeholder for the actual API call
                            # In a real environment, you would use a library like `requests`
                            # to make an asynchronous call to the Gemini API.
                            
                            # Placeholder response for demonstration
                            # simulated_response = {
                            #     "candidates": [{
                            #         "content": {
                            #             "parts": [{"text": "D'après les feedbacks, tu montres une excellente progression en dynamique, avec une bonne technique de palmage. Pour continuer à t'améliorer, pense à te concentrer sur la relaxation avant tes apnées statiques. Continue comme ça, c'est super !"}],
                            #             "role": "model"
                            #         }
                            #     }]
                            # }
                            # summary_text = simulated_response["candidates"][0]["content"]["parts"][0]["text"]

                            from google import genai

                            api_key = st.secrets["genai"]["key"]

                            client = genai.Client(api_key=api_key)

                            summary_text = client.models.generate_content(
                                model="gemini-2.0-flash",
                                contents= prompt + ': ' + all_feedback_text,
                            )

                            # print(response.text)

                            st.session_state['feedback_summary'] = summary_text.text

                        except Exception as e:
                            st.error(f"Erreur lors de la génération du résumé : {e}")

                if 'feedback_summary' in st.session_state:
                    # st.subheader(_("feedback_summary_header", lang))
                    st.write(st.session_state['feedback_summary'])

        # Tab 3: Performances by Level
        with tab_objects_main[2]:
            display_level_performance_tab(all_records_loaded, user_profiles, discipline_keys, lang)

        # Admin Tabs
        if is_admin_view_authorized:
            admin_tabs_start_index = 3
            
            # Tab 4: Club Rankings (Admin Only)
            with tab_objects_main[admin_tabs_start_index]: 
                if not all_records_loaded:
                    st.info(_("no_ranking_data", lang))
                else:
                    with st.container(border=True):
                        st.subheader(_("club_bests_subheader", lang))
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
                                translated_full_disc_name_club = _("disciplines." + disc_key_club_pb_col, lang)
                                short_disc_name_club = translated_full_disc_name_club.split('(')[0].strip() or translated_full_disc_name_club
                                display_user_club = get_display_name(user_club, user_profiles, lang) if user_club else _("anonymous_freediver_name", lang) 
                                st.metric(label=_("club_best_label", lang, discipline_short_name=short_disc_name_club), value=val_club)
                                if user_club and event_date_club:
                                    st.caption(_("achieved_at_event_on_date_caption", lang, user=display_user_club, event_name=event_name_club, event_date=event_date_club))
                                elif val_club == "N/A":
                                    st.caption(_("no_record_yet_caption", lang))

                    st.markdown("---")
                    
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
                                        "user": u_rank_tab, 
                                        "parsed_value": best_record_for_user_ranking['parsed_value'], 
                                        "event_date": session_details['event_date'], 
                                        "event_name": session_details['event_name']
                                    })
                            
                            sort_reverse_ranking = not is_lower_better(selected_discipline_ranking_key)
                            sorted_rankings_tab = sorted(user_pbs_for_discipline_ranking, key=lambda x: x['parsed_value'], reverse=sort_reverse_ranking)

                            if not sorted_rankings_tab:
                                st.info(_("no_ranking_data", lang))
                            else:
                                # Full Ranking Table
                                st.subheader(_("full_ranking_header", lang))
                                ranking_table_data = []
                                for rank_idx, rank_item in enumerate(sorted_rankings_tab):
                                    perf_display = format_seconds_to_static_time(rank_item['parsed_value']) if is_time_based_discipline(selected_discipline_ranking_key) else f"{int(rank_item['parsed_value'])}m"
                                    ranking_table_data.append({
                                        _("rank_col", lang): rank_idx + 1,
                                        _("user_col", lang): get_display_name(rank_item['user'], user_profiles, lang),
                                        _("best_performance_col", lang): perf_display,
                                        _("event_col", lang): rank_item.get('event_name', "N/A"),
                                        _("date_achieved_col", lang): rank_item.get('event_date', "N/A")
                                    })
                                st.dataframe(pd.DataFrame(ranking_table_data), use_container_width=True, hide_index=True)

            # Tab 5: Freedivers (Admin Only)
            with tab_objects_main[admin_tabs_start_index + 1]: 
                st.subheader(_("edit_freedivers_header", lang))
                
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

                freedivers_df = pd.DataFrame(freedivers_data_for_editor)
                
                edited_freedivers_df = st.data_editor(
                    freedivers_df, 
                    column_config={
                        "original_name": None,
                        _("freediver_name_col_editor", lang): st.column_config.TextColumn(required=True),
                        _("certification_col_editor", lang): st.column_config.SelectboxColumn(options=[_("no_certification_option", lang)] + list(_("certification_levels", lang).keys())),
                        _("certification_date_col_editor", lang): st.column_config.DateColumn(format="YYYY-MM-DD"),
                        _("lifras_id_col_editor", lang): st.column_config.TextColumn(),
                        _("anonymize_results_col_editor", lang): st.column_config.CheckboxColumn()
                    },
                    key="freedivers_data_editor", 
                    num_rows="dynamic", 
                    hide_index=True
                )
                
                if st.button(_("save_freedivers_changes_button", lang)):
                    edited_rows = edited_freedivers_df.to_dict('records')
                    new_profiles = {}
                    updated_records = list(all_records_loaded)
                    updated_feedback = list(instructor_feedback_loaded)
                    name_map = {}

                    all_new_names = [row[_("freediver_name_col_editor", lang)].strip() for row in edited_rows if row[_("freediver_name_col_editor", lang)]]
                    if len(all_new_names) != len(set(all_new_names)):
                        st.error("Duplicate names found in the table. Please ensure all names are unique.")
                    else:
                        for row in edited_rows:
                            original_name = row["original_name"]
                            new_name = row[_("freediver_name_col_editor", lang)].strip()
                            if not new_name: continue

                            if pd.notna(original_name) and original_name != new_name:
                                name_map[original_name] = new_name

                            cert_date = row[_("certification_date_col_editor", lang)]
                            new_profiles[new_name] = {
                                "certification": row[_("certification_col_editor", lang)],
                                "certification_date": cert_date.isoformat() if pd.notna(cert_date) else None,
                                "lifras_id": str(row[_("lifras_id_col_editor", lang)]).strip(),
                                "anonymize_results": bool(row[_("anonymize_results_col_editor", lang)])
                            }
                        
                        for rec in updated_records:
                            if rec.get("user") in name_map:
                                rec["user"] = name_map[rec["user"]]
                        
                        for fb in updated_feedback:
                            if fb.get("diver_name") in name_map:
                                fb["diver_name"] = name_map[fb["diver_name"]]
                            if fb.get("instructor_name") in name_map:
                                fb["instructor_name"] = name_map[fb["instructor_name"]]
                        
                        if st.session_state.current_user in name_map:
                            st.session_state.current_user = name_map[st.session_state.current_user]

                        save_user_profiles(new_profiles)
                        save_records(updated_records)
                        save_instructor_feedback(updated_feedback)
                        st.success(_("freedivers_updated_success", lang))
                        st.rerun()

            with tab_objects_main[admin_tabs_start_index + 2]: # Training Log
                sub_tab_sessions_view, sub_tab_sessions_edit = st.tabs([_("training_sessions_sub_tab_label", lang), _("edit_training_sessions_sub_tab_label", lang)])

                with sub_tab_sessions_view:
                    st.subheader(_("detailed_training_sessions_subheader", lang))
                    if not training_log_loaded:
                        st.info(_("no_training_sessions_logged", lang))
                    else:
                        # --- Filters ---
                        years = sorted(list(set(datetime.fromisoformat(entry['date']).year for entry in training_log_loaded if entry.get('date'))), reverse=True)
                        places = sorted(list(set(entry['place'] for entry in training_log_loaded if entry.get('place'))))
                        months_en = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                        months_translated = [_("months." + m, lang) for m in months_en]
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            selected_year = st.selectbox(_("filter_by_year_label", lang), [_("all_years_option", lang)] + years, key="training_year_filter")
                        with col2:
                            selected_month_name = st.selectbox(_("filter_by_month_label", lang), [_("all_months_option", lang)] + months_translated, key="training_month_filter")
                        with col3:
                            selected_place = st.selectbox(_("filter_by_place_label", lang), [_("all_places_option", lang)] + places, key="training_place_filter")
                        
                        # --- Filtering logic ---
                        filtered_logs = training_log_loaded
                        if selected_year != _("all_years_option", lang):
                            filtered_logs = [log for log in filtered_logs if log.get('date') and datetime.fromisoformat(log['date']).year == selected_year]
                        
                        if selected_month_name != _("all_months_option", lang):
                            month_number = months_translated.index(selected_month_name) + 1
                            filtered_logs = [log for log in filtered_logs if log.get('date') and datetime.fromisoformat(log['date']).month == month_number]
                        
                        if selected_place != _("all_places_option", lang):
                            filtered_logs = [log for log in filtered_logs if log.get('place') == selected_place]
                        
                        # --- Display logs ---
                        if not filtered_logs:
                            st.info("No training sessions match the selected filters.")
                        else:
                            for entry in sorted(filtered_logs, key=lambda x: x.get('date', '1900-01-01'), reverse=True):
                                expander_title = f"**{entry.get('date', 'N/A')} - {entry.get('place', 'N/A')}**"
                                with st.expander(expander_title, expanded=True):
                                    st.markdown(entry.get('description', _("no_description_available", lang)))

                with sub_tab_sessions_edit:
                    st.subheader(_("training_log_table_header", lang))
                    if not training_log_loaded:
                        st.info(_("no_training_sessions_logged", lang))
                    
                    training_log_display = [{"id": entry.get("id"), _("training_date_label", lang): entry.get("date"), _("training_place_label", lang): entry.get("place"), _("training_description_label", lang): entry.get("description"), _("history_delete_col_editor", lang): False} for entry in sorted(training_log_loaded, key=lambda x: x.get('date', '1900-01-01'), reverse=True)]
                    training_df_for_editor = pd.DataFrame(training_log_display)
                    if not training_df_for_editor.empty:
                        training_date_col_name = _("training_date_label", lang)
                        training_df_for_editor[training_date_col_name] = pd.to_datetime(training_df_for_editor[training_date_col_name], errors='coerce').dt.date

                        edited_training_df = st.data_editor(
                            training_df_for_editor,
                            column_config={
                                "id": None, 
                                _("training_date_label", lang): st.column_config.DateColumn(label=_("training_date_label", lang), format="YYYY-MM-DD"), 
                                _("training_place_label", lang): st.column_config.TextColumn(label=_("training_place_label", lang)), 
                                _("training_description_label", lang): st.column_config.TextColumn(label=_("training_description_label", lang)), 
                                _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(label=_("history_delete_col_editor", lang), default=False)
                            },
                            hide_index=True, key="training_log_editor", num_rows="dynamic"
                        )
                        if st.button(_("save_training_log_changes_button", lang)):
                            original_log_df = pd.DataFrame(training_log_loaded)
                            edited_log_df_copy = edited_training_df.copy()
                            edited_log_df_copy[_("training_date_label", lang)] = pd.to_datetime(edited_log_df_copy[_("training_date_label", lang)]).dt.strftime('%Y-%m-%d')
                            
                            original_log_json_str = json.dumps(sorted(original_log_df.to_dict('records'), key=lambda x: x.get('id', '')), sort_keys=True)
                            edited_log_json_str = json.dumps(sorted(edited_log_df_copy[edited_log_df_copy[_("history_delete_col_editor", lang)] == False].drop(columns=[_("history_delete_col_editor", lang)]).to_dict('records'), key=lambda x: x.get('id', '')), sort_keys=True)

                            if original_log_json_str != edited_log_json_str:
                                new_log_list = edited_log_df_copy[edited_log_df_copy[_("history_delete_col_editor", lang)] == False].drop(columns=[_("history_delete_col_editor", lang)]).to_dict('records')
                                deleted_ids = set(original_log_df['id']) - set(r['id'] for r in new_log_list if r.get('id'))
                                
                                for rec in all_records_loaded:
                                    if rec.get('linked_training_session_id') in deleted_ids:
                                        rec['linked_training_session_id'] = None
                                
                                save_training_log(new_log_list)
                                save_records(all_records_loaded)
                                st.success(_("training_log_updated_success", lang))
                                st.rerun()
                            else:
                                st.info("No changes detected in the training log.")
            
            with tab_objects_main[admin_tabs_start_index + 3]: # Performance Log
                overview_sub_tab, edit_sub_tab = st.tabs([
                    _("performances_overview_tab_label", lang),
                    _("edit_performances_sub_tab_label", lang)
                ])

                with overview_sub_tab:
                    st.subheader(_("performances_overview_tab_label", lang))
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        filter_user_perf = st.selectbox(_("filter_by_freediver_label", lang), [_("all_freedivers_option", lang)] + all_known_users_list, key="perf_log_user_filter")
                    with col2:
                        session_options = {s['id']: f"{s['date']} - {s['place']}" for s in training_log_loaded}
                        filter_session_id_perf = st.selectbox(_("filter_by_training_session_label", lang), [_("all_sessions_option", lang)] + list(session_options.keys()), format_func=lambda x: session_options.get(x, x), key="perf_log_session_filter")
                    with col3:
                        filter_discipline_perf = st.selectbox(_("filter_by_discipline_label", lang), [_("all_disciplines_option", lang)] + discipline_keys, key="perf_log_discipline_filter")

                    filtered_records = all_records_loaded
                    if filter_user_perf != _("all_freedivers_option", lang):
                        filtered_records = [r for r in filtered_records if r['user'] == filter_user_perf]
                    if filter_session_id_perf != _("all_sessions_option", lang):
                        filtered_records = [r for r in filtered_records if r.get('linked_training_session_id') == filter_session_id_perf]
                    if filter_discipline_perf != _("all_disciplines_option", lang):
                        filtered_records = [r for r in filtered_records if r['discipline'] == filter_discipline_perf]
                    
                    display_data = []
                    for rec in sorted(filtered_records, key=lambda x: x.get('entry_date', '1900-01-01'), reverse=True):
                        session_details = get_training_session_details(rec.get("linked_training_session_id"), training_log_loaded)
                        display_data.append({
                            _("user_col", lang): rec["user"],
                            _("history_discipline_col", lang): rec["discipline"],
                            _("link_training_session_label", lang): f"{session_details['event_date']} - {session_details['event_name']}",
                            _("history_performance_col", lang): rec["original_performance_str"],
                            _("history_entry_date_col", lang): rec["entry_date"]
                        })
                    st.dataframe(pd.DataFrame(display_data), hide_index=True)

                with edit_sub_tab:
                    st.subheader(_("edit_performances_sub_tab_label", lang))
                    if not all_records_loaded:
                        st.info("No performances logged in the system.")
                    else:
                        training_session_options = {log['id']: f"{log.get('date')} - {log.get('place', 'N/A')}" for log in training_log_loaded}
                        
                        perf_log_data = []
                        for rec in sorted(all_records_loaded, key=lambda x: x.get('entry_date', '1900-01-01'), reverse=True):
                            perf_log_data.append({
                                "id": rec["id"],
                                _("user_col", lang): rec["user"],
                                _("history_discipline_col", lang): rec["discipline"],
                                _("link_training_session_label", lang): training_session_options.get(rec.get("linked_training_session_id")),
                                _("history_performance_col", lang): rec["original_performance_str"],
                                _("history_delete_col_editor", lang): False
                            })

                        edited_perf_log_df = st.data_editor(
                            pd.DataFrame(perf_log_data),
                            column_config={
                                "id": None,
                                _("user_col", lang): st.column_config.SelectboxColumn(options=all_known_users_list, required=True),
                                _("history_discipline_col", lang): st.column_config.SelectboxColumn(options=discipline_keys, required=True),
                                _("link_training_session_label", lang): st.column_config.SelectboxColumn(options=list(training_session_options.values()), required=True),
                                _("history_performance_col", lang): st.column_config.TextColumn(required=True),
                                _("history_delete_col_editor", lang): st.column_config.CheckboxColumn()
                            },
                            num_rows="dynamic",
                            hide_index=True,
                            key="all_perf_editor"
                        )

                        if st.button(_("save_all_performances_button", lang)):
                            new_records = []
                            session_display_to_id = {v: k for k, v in training_session_options.items()}
                            
                            for row in edited_perf_log_df.to_dict('records'):
                                if row[_("history_delete_col_editor", lang)]:
                                    continue
                                
                                perf_str = str(row[_("history_performance_col", lang)]).strip()
                                discipline = row[_("history_discipline_col", lang)]
                                parsed_val = parse_static_time_to_seconds(perf_str, lang) if is_time_based_discipline(discipline) else parse_distance_to_meters(perf_str, lang)

                                if parsed_val is None:
                                    st.error(f"Invalid performance '{perf_str}' for user {row[_('user_col', lang)]}. Skipping.");
                                    original_rec = next((r for r in all_records_loaded if r['id'] == row['id']), None)
                                    if original_rec: new_records.append(original_rec)
                                    continue
                                
                                original_rec = next((r for r in all_records_loaded if r['id'] == row['id']), {})
                                
                                new_records.append({
                                    "id": row.get("id") or uuid.uuid4().hex,
                                    "user": row[_("user_col", lang)],
                                    "discipline": discipline,
                                    "linked_training_session_id": session_display_to_id.get(row[_("link_training_session_label", lang)]),
                                    "original_performance_str": perf_str,
                                    "parsed_value": parsed_val,
                                    "entry_date": original_rec.get('entry_date', date.today().isoformat())
                                })
                            
                            save_records(new_records)
                            st.success(_("all_performances_updated_success", lang))
                            st.rerun()

            with tab_objects_main[admin_tabs_start_index + 4]: # Feedback Log
                fb_overview_tab, fb_edit_tab = st.tabs([_("feedbacks_overview_tab_label", lang), _("edit_feedbacks_sub_tab_label", lang)])
                with fb_overview_tab:
                    st.subheader(_("feedbacks_overview_tab_label", lang))
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        filter_user = st.selectbox(_("filter_by_freediver_label", lang), [_("all_freedivers_option", lang)] + all_known_users_list, key="fb_overview_user")
                    with col2:
                        session_options = {s['id']: f"{s.get('date', 'N/A')} - {s.get('place', 'N/A')}" for s in training_log_loaded}
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
                                st.markdown(f"**{_('feedback_for_freediver_label', lang)}** {fb['diver_name']} | **{_('instructor_name_label', lang)}** {fb['instructor_name']} | **Date:** {fb['feedback_date']}")
                                styled_text = style_feedback_text(fb['feedback_text'])
                                st.markdown(styled_text, unsafe_allow_html=True)

                with fb_edit_tab:
                    st.subheader(_("feedback_log_table_header", lang))
                    if not instructor_feedback_loaded:
                        st.info(_("no_feedback_in_log", lang))
                    
                    feedback_df_data = []
                    for fb in instructor_feedback_loaded:
                        feedback_df_data.append({
                            "id": fb["id"],
                            _("feedback_date_col", lang): fb["feedback_date"],
                            _("feedback_for_freediver_label", lang): fb["diver_name"],
                            _("instructor_name_label", lang): fb["instructor_name"],
                            _("feedback_text_label", lang): fb["feedback_text"],
                            _("history_delete_col_editor", lang): False
                        })

                    feedback_df = pd.DataFrame(feedback_df_data)
                    if not feedback_df.empty:
                        date_col_name = _("feedback_date_col", lang)
                        feedback_df[date_col_name] = pd.to_datetime(feedback_df[date_col_name], errors='coerce').dt.date

                    edited_feedback_df = st.data_editor(
                        feedback_df,
                        column_config={
                            "id": None,
                            _("feedback_date_col", lang): st.column_config.DateColumn(required=True),
                            _("feedback_for_freediver_label", lang): st.column_config.SelectboxColumn(options=all_known_users_list, required=True),
                            _("instructor_name_label", lang): st.column_config.SelectboxColumn(options=all_known_users_list, required=True),
                            _("feedback_text_label", lang): st.column_config.TextColumn(required=True),
                            _("history_delete_col_editor", lang): st.column_config.CheckboxColumn()
                        },
                        num_rows="dynamic",
                        hide_index=True,
                        key="feedback_log_editor"
                    )

                    if st.button(_("save_feedback_log_changes_button", lang)):
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
                                    "training_session_id": None # This needs to be linked if you want to edit it here
                                })
                        save_instructor_feedback(new_feedback_list)
                        st.success(_("feedback_log_updated_success", lang))
                        st.rerun()

if __name__ == "__main__":
    main()
