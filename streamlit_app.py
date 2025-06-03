import streamlit as st
import pandas as pd
import json
from datetime import datetime, date, time
import uuid # Added for unique record IDs
import altair as alt # Added for advanced charting

RECORDS_FILE = "freediving_records.json"
USER_PROFILES_FILE = "user_profiles.json" 
TRAINING_LOG_FILE = "training_log.json" 

# --- Language Translations ---
TRANSLATIONS = {
    "en": {
        "page_title": "Freediving Logbook",
        "app_title": "🌊 Freediving Performance Tracker",
        "user_management_header": "👤 User Management",
        "no_users_yet": "No users yet. Add a new user to begin.",
        "enter_new_user_name": "Enter New User Name (Format: Firstname L.)", 
        "new_user_success": "New user: **{user}**. You can now log performances.",
        "select_user_or_add": "Select User or Add New",
        "add_new_user_option": "✨ Add New User...",
        "existing_user_selected": "Existing user **{user}** selected.",
        "log_performance_header": "✏️ Log New Performance",
        "profile_header_sidebar": "🪪 Diver Profile", 
        "select_user_first_warning": "Select or add a user first to log performances.",
        "logging_for": "Logging for: **{user}**",
        "date_of_performance": "Date of Performance",
        "discipline": "Discipline",
        "performance_value": "Performance Value",
        "sta_help": "Format: MM:SS (e.g., 03:45). Milliseconds will be ignored for display.", 
        "dyn_depth_help": "Format: Number, optionally followed by 'm' (e.g., 75 or 75m)",
        "save_performance_button": "💾 Save Performance",
        "performance_value_empty_error": "Performance value cannot be empty.",
        "performance_saved_success": "Performance saved for {user}!",
        "process_performance_error": "Failed to process performance value. Please check format.",
        "records_for_header": "📊 Records for {user}", 
        "personal_records_tab_main_title": "👤 Personal Records", 
        "select_user_to_view_personal_records": "Please select a user from the sidebar to view their personal records.",
        "no_performances_yet": "No performances logged yet for this user. Add some using the sidebar!",
        "personal_bests_subheader": "🏆 Personal Bests",
        "club_bests_subheader": "🌟 Club Best Performances", 
        "pb_label": "PB {discipline_short_name}",
        "club_best_label": "Club Best {discipline_short_name}", 
        "achieved_by_on_caption": "By {user} on {date}", 
        "achieved_on_caption": "Achieved on: {date}",
        "no_record_yet_caption": "No record yet",
        "performance_evolution_subheader": "📈 Performance Evolution",
        "seconds_unit": "seconds",
        "meters_unit": "meters",
        "history_table_subheader": "📜 History Table (Editable)", 
        "full_history_subheader": "📜 Full History",
        "history_date_col": "Date",
        "history_discipline_col": "Discipline", 
        "history_performance_col": "Performance",
        "history_actions_col": "Actions", 
        "history_delete_col_editor": "Delete?", 
        "no_history_display": "No history to display for this discipline.",
        "no_data_for_graph": "No data to display graph for this discipline.",
        "welcome_message": "👋 Welcome to the Freediving Tracker! Please add your first user in the sidebar to get started.",
        "select_user_prompt": "Please select a user from the sidebar, or add a new one, to view and log performances.", 
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
            "16x25m Speed Endurance": "16x25m Speed Endurance" 
        },
        "ranking_tab_title": "🏆 General Rankings",
        "select_discipline_for_ranking": "Select discipline for ranking:",
        "podium_header": "🥇🥈🥉 Podium",
        "full_ranking_header": "📋 Full Ranking",
        "rank_col": "Rank",
        "user_col": "User",
        "best_performance_col": "Best Performance",
        "date_achieved_col": "Date Achieved",
        "no_ranking_data": "No ranking data available for this discipline yet.",
        "profile_tab_title": "🪪 Diver Profile", 
        "certification_label": "Certification Level:",
        "certification_date_label": "Certification Date:", 
        "lifras_id_label": "LIFRAS ID:", 
        "save_profile_button": "💾 Save Profile",
        "profile_saved_success": "Profile saved successfully for {user}!",
        "select_user_to_edit_profile": "Select a user from the sidebar to view or edit their profile.", 
        "no_certification_option": "Not Specified",
        "certification_levels": { 
            "A1": "A1", "A2": "A2", "A3": "A3", 
            "I1": "I1", "I2": "I2", "I3": "I3"
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
        "delete_confirmation_prompt": "Are you sure you want to delete this performance: {date} - {performance}?", 
        "performance_deleted_success": "Performance deleted successfully.",
        "no_record_found_for_editing": "Error: Could not find the record to edit.",
        "performance_updated_success": "Performance updated successfully.",
        "history_updated_success": "History updated successfully.",
        "critical_error_edit_id_not_found": "Critical error: Record ID '{record_id}' to edit not found in master list. Edit cancelled.",
        "club_performances_tab_title": "📈 Club Performances",
        "no_data_for_club_performance_display": "No performance data available for the club in this discipline.",
        "quarterly_average_label": "Quarterly Average",
        "divers_tab_title": "🫂 Divers",
        "edit_divers_header": "Edit Diver Information",
        "diver_name_col_editor": "Diver Name (First L.)", 
        "certification_col_editor": "Certification Level",
        "certification_date_col_editor": "Cert. Date", 
        "lifras_id_col_editor": "LIFRAS ID", 
        "pb_sta_col_editor": "PB STA",
        "pb_dynbf_col_editor": "PB DYN-BF",
        "pb_depth_col_editor": "PB Depth",
        "pb_16x25_col_editor": "PB 16x25m",
        "save_divers_changes_button": "💾 Save Diver Changes",
        "divers_updated_success": "Diver data updated successfully.",
        "name_conflict_error": "Error: Name '{new_name}' is already in use by another diver. Please choose a unique name.",
        "original_name_col_editor_hidden": "original_name", 
        "certification_summary_header": "🔢 Divers per Certification Level",
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
        "training_log_updated_success": "Training log updated successfully."
    },
    "fr": {
        "page_title": "Carnet d'Apnée",
        "app_title": "🌊 Suivi des Performances d'Apnée",
        "user_management_header": "👤 Gestion des Utilisateurs",
        "no_users_yet": "Aucun utilisateur pour le moment. Ajoutez un nouvel utilisateur pour commencer.",
        "enter_new_user_name": "Entrez le nom du nouvel utilisateur (Format: Prénom L.)", 
        "new_user_success": "Nouvel utilisateur : **{user}**. Vous pouvez maintenant enregistrer des performances.",
        "select_user_or_add": "Sélectionnez un utilisateur ou ajoutez-en un nouveau",
        "add_new_user_option": "✨ Ajouter un nouvel utilisateur...",
        "existing_user_selected": "Utilisateur existant **{user}** sélectionné.",
        "log_performance_header": "✏️ Enregistrer une nouvelle performance",
        "profile_header_sidebar": "🪪 Profil Apnéiste", 
        "select_user_first_warning": "Sélectionnez ou ajoutez d'abord un utilisateur pour enregistrer des performances.",
        "logging_for": "Enregistrement pour : **{user}**",
        "date_of_performance": "Date de la performance",
        "discipline": "Discipline",
        "performance_value": "Valeur de la performance",
        "sta_help": "Format : MM:SS (ex: 03:45). Les millisecondes seront ignorées à l'affichage.", 
        "dyn_depth_help": "Format : Nombre, optionnellement suivi de 'm' (ex: 75 ou 75m)",
        "save_performance_button": "💾 Enregistrer la performance",
        "performance_value_empty_error": "La valeur de la performance ne peut pas être vide.",
        "performance_saved_success": "Performance enregistrée pour {user} !",
        "process_performance_error": "Échec du traitement de la valeur de performance. Veuillez vérifier le format.",
        "records_for_header": "📊 Records pour {user}",
        "personal_records_tab_main_title": "👤 Records Personnels",
        "select_user_to_view_personal_records": "Veuillez sélectionner un utilisateur dans la barre latérale pour voir ses records personnels.",
        "no_performances_yet": "Aucune performance enregistrée pour cet utilisateur. Ajoutez-en via la barre latérale !",
        "personal_bests_subheader": "🏆 Records Personnels",
        "club_bests_subheader": "🌟 Meilleures Performances du Club", 
        "pb_label": "RP {discipline_short_name}",
        "club_best_label": "Record Club {discipline_short_name}", 
        "achieved_by_on_caption": "Par {user} le {date}", 
        "achieved_on_caption": "Réalisé le : {date}",
        "no_record_yet_caption": "Aucun record pour l'instant",
        "performance_evolution_subheader": "📈 Évolution des Performances",
        "seconds_unit": "secondes",
        "meters_unit": "mètres",
        "history_table_subheader": "📜 Tableau de l'Historique (Modifiable)", 
        "full_history_subheader": "📜 Historique Complet",
        "history_date_col": "Date",
        "history_discipline_col": "Discipline",
        "history_performance_col": "Performance",
        "history_actions_col": "Actions",
        "history_delete_col_editor": "Supprimer ?", 
        "no_history_display": "Aucun historique à afficher pour cette discipline.",
        "no_data_for_graph": "Aucune donnée à afficher pour le graphique de cette discipline.",
        "welcome_message": "👋 Bienvenue sur le Suivi d'Apnée ! Veuillez ajouter votre premier utilisateur dans la barre latérale pour commencer.",
        "select_user_prompt": "Veuillez sélectionner un utilisateur dans la barre latérale, ou en ajouter un nouveau, pour voir et enregistrer les performances.",
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
            "16x25m Speed Endurance": "16x25m Vitesse Endurance" 
        },
        "ranking_tab_title": "🏆 Classement Général",
        "select_discipline_for_ranking": "Sélectionnez la discipline pour le classement :",
        "podium_header": "🥇🥈🥉 Podium",
        "full_ranking_header": "📋 Classement Complet",
        "rank_col": "Rang",
        "user_col": "Utilisateur",
        "best_performance_col": "Meilleure Performance",
        "date_achieved_col": "Date d'obtention",
        "no_ranking_data": "Aucune donnée de classement disponible pour cette discipline pour le moment.",
        "profile_tab_title": "🪪 Profil Apnéiste", 
        "certification_label": "Niveau de Brevet :",
        "certification_date_label": "Date du Brevet :", 
        "lifras_id_label": "ID LIFRAS :", 
        "save_profile_button": "💾 Enregistrer le Profil",
        "profile_saved_success": "Profil enregistré avec succès pour {user} !",
        "select_user_to_edit_profile": "Sélectionnez un utilisateur dans la barre latérale pour voir ou modifier son profil.",
        "no_certification_option": "Non Spécifié",
        "certification_levels": { 
            "A1": "A1", "A2": "A2", "A3": "A3", 
            "I1": "I1", "I2": "I2", "I3": "I3"
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
        "delete_confirmation_prompt": "Êtes-vous sûr de vouloir supprimer cette performance : {date} - {performance} ?",
        "performance_deleted_success": "Performance supprimée avec succès.",
        "no_record_found_for_editing": "Erreur : Impossible de trouver l'enregistrement à modifier.",
        "performance_updated_success": "Performance mise à jour avec succès.",
        "history_updated_success": "Historique mis à jour avec succès.",
        "critical_error_edit_id_not_found": "Erreur critique : ID d'enregistrement '{record_id}' à modifier non trouvé dans la liste principale. Modification annulée.",
        "club_performances_tab_title": "📈 Performances du Club",
        "no_data_for_club_performance_display": "Aucune donnée de performance disponible pour le club dans cette discipline.",
        "quarterly_average_label": "Moyenne Trimestrielle",
        "divers_tab_title": "🫂 Apnéistes",
        "edit_divers_header": "Modifier les Informations des Apnéistes",
        "diver_name_col_editor": "Nom Apnéiste (Prénom L.)", 
        "certification_col_editor": "Niveau de Brevet",
        "certification_date_col_editor": "Date Brevet", 
        "lifras_id_col_editor": "ID LIFRAS", 
        "pb_sta_col_editor": "RP STA",
        "pb_dynbf_col_editor": "RP DYN-BF",
        "pb_depth_col_editor": "RP Profondeur",
        "pb_16x25_col_editor": "RP 16x25m",
        "save_divers_changes_button": "💾 Sauvegarder les Apnéistes",
        "divers_updated_success": "Données des apnéistes mises à jour avec succès.",
        "name_conflict_error": "Erreur : Le nom '{new_name}' est déjà utilisé par un autre apnéiste. Veuillez choisir un nom unique.",
        "original_name_col_editor_hidden": "nom_original",
        "certification_summary_header": "🔢 Apnéistes par Niveau de Brevet",
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
        "training_log_updated_success": "Journal d'entraînement mis à jour avec succès."
    },
    "nl": {
        "page_title": "Vrijduik Logboek",
        "app_title": "🌊 Vrijduik Prestatie Tracker",
        "user_management_header": "👤 Gebruikersbeheer",
        "no_users_yet": "Nog geen gebruikers. Voeg een nieuwe gebruiker toe om te beginnen.",
        "enter_new_user_name": "Voer nieuwe gebruikersnaam in (Formaat: Voornaam L.)", 
        "new_user_success": "Nieuwe gebruiker: **{user}**. U kunt nu prestaties loggen.",
        "select_user_or_add": "Selecteer gebruiker of voeg nieuwe toe",
        "add_new_user_option": "✨ Nieuwe gebruiker toevoegen...",
        "existing_user_selected": "Bestaande gebruiker **{user}** geselecteerd.",
        "log_performance_header": "✏️ Log Nieuwe Prestatie",
        "profile_header_sidebar": "🪪 Duikersprofiel", 
        "select_user_first_warning": "Selecteer of voeg eerst een gebruiker toe om prestaties te loggen.",
        "logging_for": "Loggen voor: **{user}**",
        "date_of_performance": "Datum van prestatie",
        "discipline": "Discipline",
        "performance_value": "Prestatiewaarde",
        "sta_help": "Formaat: MM:SS (bijv. 03:45). Milliseconden worden genegeerd voor weergave.", 
        "dyn_depth_help": "Formaat: Getal, optioneel gevolgd door 'm' (bijv. 75 of 75m)",
        "save_performance_button": "💾 Prestatie Opslaan",
        "performance_value_empty_error": "Prestatiewaarde mag niet leeg zijn.",
        "performance_saved_success": "Prestatie opgeslagen voor {user}!",
        "process_performance_error": "Kon prestatiewaarde niet verwerken. Controleer het formaat.",
        "records_for_header": "📊 Records voor {user}",
        "personal_records_tab_main_title": "👤 Persoonlijke Records",
        "select_user_to_view_personal_records": "Selecteer een gebruiker in de zijbalk om persoonlijke records te bekijken.",
        "no_performances_yet": "Nog geen prestaties gelogd voor deze gebruiker. Voeg er enkele toe via de zijbalk!",
        "personal_bests_subheader": "🏆 Persoonlijke Records",
        "club_bests_subheader": "🌟 Club Beste Prestaties", 
        "pb_label": "PR {discipline_short_name}",
        "club_best_label": "Clubrecord {discipline_short_name}", 
        "achieved_by_on_caption": "Door {user} op {date}", 
        "achieved_on_caption": "Behaald op: {date}",
        "no_record_yet_caption": "Nog geen record",
        "performance_evolution_subheader": "📈 Prestatie-evolutie",
        "seconds_unit": "seconden",
        "meters_unit": "meter",
        "history_table_subheader": "📜 Geschiedenistabel (Bewerkbaar)", 
        "full_history_subheader": "📜 Volledige Geschiedenis",
        "history_date_col": "Datum",
        "history_discipline_col": "Discipline",
        "history_performance_col": "Prestatie",
        "history_actions_col": "Acties",
        "history_delete_col_editor": "Verwijderen?", 
        "no_history_display": "Geen geschiedenis om weer te geven voor deze discipline.",
        "no_data_for_graph": "Geen gegevens om grafiek weer te geven voor deze discipline.",
        "welcome_message": "👋 Welkom bij de Vrijduik Tracker! Voeg uw eerste gebruiker toe in de zijbalk om te beginnen.",
        "select_user_prompt": "Selecteer een gebruiker in de zijbalk, of voeg een nieuwe toe, om prestaties te bekijken en te loggen.",
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
            "16x25m Speed Endurance": "16x25m Snelheid Uithouding" 
        },
        "ranking_tab_title": "🏆 Algemeen Klassement",
        "select_discipline_for_ranking": "Selecteer discipline voor klassement:",
        "podium_header": "🥇🥈🥉 Podium",
        "full_ranking_header": "📋 Volledig Klassement",
        "rank_col": "Rang",
        "user_col": "Gebruiker",
        "best_performance_col": "Beste Prestatie",
        "date_achieved_col": "Datum Behaald",
        "no_ranking_data": "Nog geen klassementgegevens beschikbaar voor deze discipline.",
        "profile_tab_title": "🪪 Duikersprofiel", 
        "certification_label": "Certificeringsniveau:",
        "certification_date_label": "Certificatiedatum:", 
        "lifras_id_label": "LIFRAS ID:", 
        "save_profile_button": "💾 Profiel Opslaan",
        "profile_saved_success": "Profiel succesvol opgeslagen voor {user}!",
        "select_user_to_edit_profile": "Selecteer een gebruiker in de zijbalk om hun profiel te bekijken of te bewerken.",
        "no_certification_option": "Niet Gespecificeerd",
        "certification_levels": { 
            "A1": "A1", "A2": "A2", "A3": "A3", 
            "I1": "I1", "I2": "I2", "I3": "I3"
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
        "delete_confirmation_prompt": "Weet u zeker dat u deze prestatie wilt verwijderen: {date} - {performance}?",
        "performance_deleted_success": "Prestatie succesvol verwijderd.",
        "no_record_found_for_editing": "Fout: Kon de te bewerken record niet vinden.",
        "performance_updated_success": "Prestatie succesvol bijgewerkt.",
        "history_updated_success": "Geschiedenis succesvol bijgewerkt.",
        "critical_error_edit_id_not_found": "Kritieke fout: Record-ID '{record_id}' om te bewerken niet gevonden in hoofdlijst. Bewerken geannuleerd.",
        "club_performances_tab_title": "📈 Clubprestaties",
        "no_data_for_club_performance_display": "Geen prestatiegegevens beschikbaar voor de club in deze discipline.",
        "quarterly_average_label": "Kwartaalgemiddelde",
        "divers_tab_title": "🫂 Duikers",
        "edit_divers_header": "Duikerinformatie Bewerken",
        "diver_name_col_editor": "Naam Duiker (Voornaam L.)", 
        "certification_col_editor": "Certificeringsniveau",
        "certification_date_col_editor": "Cert. Datum", 
        "lifras_id_col_editor": "LIFRAS ID", 
        "pb_sta_col_editor": "PR STA",
        "pb_dynbf_col_editor": "PR DYN-BF",
        "pb_depth_col_editor": "PR Diepte",
        "pb_16x25_col_editor": "PR 16x25m",
        "save_divers_changes_button": "💾 Duikers Opslaan",
        "divers_updated_success": "Duikergegevens succesvol bijgewerkt.",
        "name_conflict_error": "Fout: Naam '{new_name}' is al in gebruik door een andere duiker. Kies een unieke naam.",
        "original_name_col_editor_hidden": "originele_naam",
        "certification_summary_header": "🔢 Duikers per Certificatieniveau",
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
        "training_log_updated_success": "Trainingslogboek succesvol bijgewerkt."
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
            print(f"Warning: Translation key '{key}' not found in '{lang}' or 'en'.")
            return key


# --- Data Handling for Performance Records ---
def ensure_record_ids(records_list):
    """Ensures all records have a unique ID, adding one if missing."""
    updated = False
    for record in records_list:
        if record.get('id') is None:
            record['id'] = uuid.uuid4().hex
            updated = True
    return updated

def load_records():
    """Loads performance records from the JSON file and ensures IDs."""
    try:
        with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
            records = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        records = [] 
    
    if ensure_record_ids(records):
        save_records(records) 
    return records

def save_records(records):
    """Saves performance records to the JSON file."""
    with open(RECORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=4, ensure_ascii=False) 

# --- Data Handling for User Profiles ---
def load_user_profiles():
    """Loads user profiles from the JSON file."""
    try:
        with open(USER_PROFILES_FILE, 'r', encoding='utf-8') as f:
            profiles = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        profiles = {} 
    return profiles

def save_user_profiles(profiles):
    """Saves user profiles to the JSON file."""
    with open(USER_PROFILES_FILE, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=4, ensure_ascii=False)

# --- Data Handling for Training Logs ---
def ensure_training_log_ids(log_list):
    """Ensures all training logs have a unique ID."""
    updated = False
    for entry in log_list:
        if entry.get('id') is None:
            entry['id'] = uuid.uuid4().hex
            updated = True
    return updated

def load_training_log():
    """Loads training logs from the JSON file and ensures IDs."""
    try:
        with open(TRAINING_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        logs = []
    if ensure_training_log_ids(logs):
        save_training_log(logs)
    return logs

def save_training_log(logs):
    """Saves training logs to the JSON file."""
    with open(TRAINING_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)


# --- Performance Parsing and Formatting ---
def is_time_based_discipline(discipline_key):
    """Checks if a discipline's performance is time-based."""
    return discipline_key in ["Static Apnea (STA)", "16x25m Speed Endurance"]

def parse_static_time_to_seconds(time_str, lang='en'):
    try:
        parts = time_str.split(':')
        if len(parts) != 2: 
            st.error(_("invalid_time_format", lang, time_str=time_str))
            return None
        minutes = int(parts[0])
        sec_ms_part = parts[1]
        if '.' in sec_ms_part: # Input might still have ms, parse them
            sec_parts = sec_ms_part.split('.')
            if len(sec_parts) != 2: 
                st.error(_("invalid_ms_format", lang, time_str=time_str))
                return None
            seconds = int(sec_parts[0])
            # Take only up to 3 digits for milliseconds if provided
            milliseconds_str = sec_parts[1][:3].ljust(3, '0') 
            milliseconds = int(milliseconds_str)
            total_seconds = minutes * 60 + seconds + milliseconds / 1000.0
        else:
            seconds = int(sec_ms_part)
            total_seconds = float(minutes * 60 + seconds)
        if not (0 <= minutes and 0 <= seconds < 60 and (0 <= milliseconds < 1000 if '.' in sec_ms_part else True)):
             st.error(_("time_values_out_of_range", lang, time_str=time_str))
             return None
        return total_seconds
    except ValueError:
        st.error(_("could_not_parse_time", lang, time_str=time_str))
        return None

def format_seconds_to_static_time(total_seconds_float):
    """Formats total seconds (float) to MM:SS string, ignoring milliseconds."""
    if total_seconds_float is None or pd.isna(total_seconds_float): return "N/A"
    total_seconds_float = float(total_seconds_float) 
    
    # Round to the nearest second for display
    rounded_total_seconds = round(total_seconds_float)

    minutes = int(rounded_total_seconds // 60)
    seconds = int(rounded_total_seconds % 60)
    
    return f"{minutes:02d}:{seconds:02d}"


def parse_distance_to_meters(dist_str, lang='en'):
    try:
        cleaned_dist_str = dist_str.lower().replace('m', '').strip()
        if not cleaned_dist_str: 
            st.error(_("distance_empty_error", lang))
            return None
        val = int(cleaned_dist_str)
        if val < 0:
            st.error(_("distance_negative_error", lang))
            return None
        return val
    except ValueError:
        st.error(_("invalid_distance_format", lang, dist_str=dist_str))
        return None

# --- Main App ---
def main():
    if 'language' not in st.session_state:
        st.session_state.language = 'en'  
    if 'initiate_clear_training_inputs' not in st.session_state:
        st.session_state.initiate_clear_training_inputs = False
    
    lang = st.session_state.language

    if st.session_state.initiate_clear_training_inputs:
        st.session_state.training_description = ""  
        st.session_state.training_place = "Blocry"    
        st.session_state.initiate_clear_training_inputs = False 

    st.set_page_config(page_title=_("page_title", lang), layout="wide", initial_sidebar_state="expanded")
    st.title(_("app_title", lang))

    language_options = {"English": "en", "Français": "fr", "Nederlands": "nl"}
    current_lang_display_name = [k_disp for k_disp, v_code in language_options.items() if v_code == lang][0]
    selected_lang_display_name = st.sidebar.selectbox(
        "language_selector_internal_label", 
        options=list(language_options.keys()),
        index=list(language_options.keys()).index(current_lang_display_name), 
        key="language_selector_widget",
        label_visibility="collapsed" 
    )
    new_lang_code = language_options[selected_lang_display_name]
    if st.session_state.language != new_lang_code:
        st.session_state.language = new_lang_code
        st.rerun() 
    lang = st.session_state.language 

    all_records_loaded = load_records() 
    user_profiles = load_user_profiles() 
    training_log_loaded = load_training_log() 

    discipline_keys = ["Static Apnea (STA)", "Dynamic Bi-fins (DYN-BF)", "Depth (CWT/FIM)", "16x25m Speed Endurance"] 
    translated_disciplines_for_display = [_("disciplines." + key, lang) for key in discipline_keys]

    st.sidebar.header(_("user_management_header", lang))
    users_from_records = set(r['user'] for r in all_records_loaded)
    users_from_profiles = set(user_profiles.keys())
    all_known_users_set = users_from_records.union(users_from_profiles)
    all_known_users_list = sorted(list(all_known_users_set)) if all_known_users_set else []
    
    current_user = None
    if all_known_users_list:
        user_options_sidebar = [_("add_new_user_option", lang)] + all_known_users_list
        default_user_for_selectbox = st.session_state.get("current_user_sidebar_selection", user_options_sidebar[1] if len(user_options_sidebar) > 1 else user_options_sidebar[0])
        try:
            default_selection_index_sidebar = user_options_sidebar.index(default_user_for_selectbox)
        except ValueError: 
            default_selection_index_sidebar = 1 if all_known_users_list else 0

        selected_option_sidebar = st.sidebar.selectbox(
            _("select_user_or_add", lang), 
            user_options_sidebar, 
            index=default_selection_index_sidebar, 
            key="user_selection_dropdown_widget" 
        )
        st.session_state.current_user_sidebar_selection = selected_option_sidebar 

        if selected_option_sidebar == _("add_new_user_option", lang):
            new_user_name_input_sidebar = st.sidebar.text_input(_("enter_new_user_name", lang), key="new_user_existing_list_input").strip()
            if new_user_name_input_sidebar:
                current_user = new_user_name_input_sidebar
                if current_user in all_known_users_list:
                     st.sidebar.info(_("existing_user_selected", lang, user=current_user))
                else: 
                     st.sidebar.success(_("new_user_success", lang, user=current_user).split('.')[0] + ". Log a performance or save profile to confirm.")
                     if current_user not in user_profiles:
                         user_profiles[current_user] = {"certification": _("no_certification_option", lang), "certification_date": None, "lifras_id": ""} 
        else:
            current_user = selected_option_sidebar
    else: 
        st.sidebar.info(_("no_users_yet", lang))
        new_user_name_input_sidebar = st.sidebar.text_input(_("enter_new_user_name", lang), key="new_user_empty_list_input").strip()
        if new_user_name_input_sidebar:
            current_user = new_user_name_input_sidebar
            st.sidebar.success(_("new_user_success", lang, user=current_user).split('.')[0] + ". Log a performance or save profile.")
            if current_user not in user_profiles: 
                user_profiles[current_user] = {"certification": _("no_certification_option", lang), "certification_date": None, "lifras_id": ""}

    st.session_state.current_user = current_user

    st.sidebar.header(_("log_performance_header", lang))
    if not current_user:
        st.sidebar.warning(_("select_user_first_warning", lang))
    else:
        st.sidebar.write(_("logging_for", lang, user=current_user))
        log_date_input_val = st.sidebar.date_input(_("date_of_performance", lang), date.today(), key="log_date_input_perf") 
        selected_translated_discipline = st.sidebar.selectbox(
            _("discipline", lang), 
            translated_disciplines_for_display, 
            key="log_discipline_select"
        )
        log_discipline_original_key = None 
        for key_iter in discipline_keys: 
            if _("disciplines." + key_iter, lang) == selected_translated_discipline:
                log_discipline_original_key = key_iter
                break
        
        performance_help_text = ""
        if is_time_based_discipline(log_discipline_original_key):
            performance_help_text = _("sta_help", lang)
        elif log_discipline_original_key in ["Dynamic Bi-fins (DYN-BF)", "Depth (CWT/FIM)"]: 
            performance_help_text = _("dyn_depth_help", lang)
        
        log_performance_str = st.sidebar.text_input(_("performance_value", lang), help=performance_help_text, key="log_performance_input").strip()

        if st.sidebar.button(_("save_performance_button", lang), key="save_performance_button"):
            if not log_performance_str: st.sidebar.error(_("performance_value_empty_error", lang))
            elif not log_discipline_original_key: st.sidebar.error("Internal error: Discipline key not found.") 
            else:
                valid_input = True
                parsed_value_for_storage = None
                if is_time_based_discipline(log_discipline_original_key):
                    parsed_value_for_storage = parse_static_time_to_seconds(log_performance_str, lang)
                else: 
                    parsed_value_for_storage = parse_distance_to_meters(log_performance_str, lang)
                
                if parsed_value_for_storage is None: 
                     valid_input = False
                
                if valid_input:
                    new_record = {
                        "id": uuid.uuid4().hex, 
                        "user": current_user, "date": log_date_input_val.isoformat(),
                        "discipline": log_discipline_original_key, 
                        "original_performance_str": log_performance_str,
                        "parsed_value": parsed_value_for_storage}
                    all_records_loaded.append(new_record) 
                    save_records(all_records_loaded)    
                    if current_user not in user_profiles: 
                        user_profiles[current_user] = {"certification": _("no_certification_option", lang), "certification_date": None, "lifras_id": ""}
                        save_user_profiles(user_profiles)
                    st.sidebar.success(_("performance_saved_success", lang, user=current_user))
                    st.rerun() 
                elif parsed_value_for_storage is None and log_performance_str: 
                    pass 
                elif not log_performance_str: 
                    pass
    
    # --- Log New Training Session ---
    st.sidebar.markdown("---")
    st.sidebar.header(_("log_training_header_sidebar", lang))
    training_date_log_val = st.sidebar.date_input(_("training_date_label", lang), date.today(), key="training_date_input_widget") 
    
    if "training_place" not in st.session_state:
        st.session_state.training_place = "Blocry" 
    st.sidebar.text_input(_("training_place_label", lang), key="training_place")
    
    if "training_description" not in st.session_state:
        st.session_state.training_description = ""
    st.sidebar.text_area(_("training_description_label", lang), key="training_description")

    if st.sidebar.button(_("save_training_button", lang), key="save_training_actual_button"): 
        desc_to_save = st.session_state.training_description
        place_to_save = st.session_state.training_place

        if not desc_to_save.strip():
            st.sidebar.error(_("training_description_empty_error", lang))
        else:
            new_training_entry = {
                "id": uuid.uuid4().hex,
                "date": training_date_log_val.isoformat(), 
                "place": place_to_save.strip(),
                "description": desc_to_save.strip()
            }
            training_log_loaded.append(new_training_entry)
            save_training_log(training_log_loaded)
            st.sidebar.success(_("training_session_saved_success", lang))
            st.session_state.initiate_clear_training_inputs = True
            st.rerun()


    # --- Profile Section in Sidebar ---
    if current_user:
        st.sidebar.markdown("---") 
        st.sidebar.header(_("profile_header_sidebar", lang))
        user_profile_data_sidebar = user_profiles.get(current_user, {})
        
        current_certification_sidebar = user_profile_data_sidebar.get("certification", _("no_certification_option", lang))
        cert_level_keys_from_dict_sidebar = list(TRANSLATIONS[lang]["certification_levels"].keys()) 
        actual_selectbox_options_sidebar = [_("no_certification_option", lang)] + cert_level_keys_from_dict_sidebar
        try:
            current_cert_index_sidebar = actual_selectbox_options_sidebar.index(current_certification_sidebar)
        except ValueError: 
            current_cert_index_sidebar = 0 
        new_certification_sidebar = st.sidebar.selectbox(
            _("certification_label", lang),
            options=actual_selectbox_options_sidebar,
            index=current_cert_index_sidebar,
            key="certification_select_sidebar" 
        )

        current_cert_date_str_sidebar = user_profile_data_sidebar.get("certification_date")
        current_cert_date_obj_sidebar = None
        if current_cert_date_str_sidebar:
            try:
                current_cert_date_obj_sidebar = date.fromisoformat(current_cert_date_str_sidebar)
            except ValueError:
                current_cert_date_obj_sidebar = None 
        
        new_cert_date_sidebar = st.sidebar.date_input(
            _("certification_date_label", lang), 
            value=current_cert_date_obj_sidebar, 
            key="cert_date_sidebar"
        )
        
        current_lifras_id_sidebar = user_profile_data_sidebar.get("lifras_id", "")
        new_lifras_id_sidebar = st.sidebar.text_input(
            _("lifras_id_label", lang), 
            value=current_lifras_id_sidebar, 
            key="lifras_id_sidebar"
        )

        if st.sidebar.button(_("save_profile_button", lang), key="save_profile_btn_sidebar"):
            user_profiles.setdefault(current_user, {})["certification"] = new_certification_sidebar
            user_profiles[current_user]["certification_date"] = new_cert_date_sidebar.isoformat() if new_cert_date_sidebar else None
            user_profiles[current_user]["lifras_id"] = new_lifras_id_sidebar.strip()
            save_user_profiles(user_profiles)
            st.sidebar.success(_("profile_saved_success", lang, user=current_user))
    

    # --- Main Display Area with Top-Level Tabs ---
    personal_records_tab_name = _("personal_records_tab_main_title", lang)
    if current_user: 
        personal_records_tab_name = _("records_for_header", lang, user=current_user)
    
    ranking_tab_name = _("ranking_tab_title", lang)
    club_perf_tab_name = _("club_performances_tab_title", lang) 
    divers_tab_name = _("divers_tab_title", lang) 
    training_log_main_tab_name = _("training_log_tab_title", lang) 

    if not all_records_loaded and not all_known_users_list and not current_user and not training_log_loaded: 
        st.info(_("welcome_message", lang))
    else:
        # The Profile tab is removed from here as it's in the sidebar
        tab_personal, tab_ranking, tab_club_perf, tab_divers, tab_training = st.tabs(
            [personal_records_tab_name, ranking_tab_name, club_perf_tab_name, divers_tab_name, training_log_main_tab_name]
        )

        with tab_personal:
            if current_user:
                user_records_for_tab = [r for r in all_records_loaded if r['user'] == current_user]
                if not user_records_for_tab:
                    st.info(_("no_performances_yet", lang))
                else:
                    with st.container(border=True): # Added border
                        # st.markdown("<div style='background-color: #ffffe0; padding: 10px; border-radius: 5px; margin-bottom:10px;'>", unsafe_allow_html=True) # Removed
                        st.subheader(_("personal_bests_subheader", lang))
                        pbs_tab = {} 
                        for disc_key_pb_tab in discipline_keys:
                            disc_records_pb_tab = [r_pb_tab for r_pb_tab in user_records_for_tab if r_pb_tab['discipline'] == disc_key_pb_tab and r_pb_tab.get('parsed_value') is not None]
                            if not disc_records_pb_tab:
                                pbs_tab[disc_key_pb_tab] = ("N/A", None) 
                                continue
                            
                            if disc_key_pb_tab == "16x25m Speed Endurance": 
                                 best_record_pb_tab = min(disc_records_pb_tab, key=lambda x_pb_tab: x_pb_tab['parsed_value'])
                            else: 
                                 best_record_pb_tab = max(disc_records_pb_tab, key=lambda x_pb_tab: x_pb_tab['parsed_value'])
                            
                            if is_time_based_discipline(disc_key_pb_tab):
                                pb_value_formatted_tab = format_seconds_to_static_time(best_record_pb_tab['parsed_value'])
                            else:
                                pb_value_formatted_tab = f"{best_record_pb_tab['parsed_value']}m"
                            pbs_tab[disc_key_pb_tab] = (pb_value_formatted_tab, best_record_pb_tab['date'])

                        cols_pb_tab = st.columns(len(discipline_keys))
                        for i_pb_col_tab, disc_key_pb_col_tab in enumerate(discipline_keys):
                            val_tab, dt_tab = pbs_tab.get(disc_key_pb_col_tab, ("N/A", None))
                            with cols_pb_tab[i_pb_col_tab]:
                                translated_full_discipline_name_tab = _("disciplines." + disc_key_pb_col_tab, lang)
                                short_disc_name_tab = translated_full_discipline_name_tab.split('(')[0].strip()
                                if not short_disc_name_tab: 
                                    short_disc_name_tab = translated_full_discipline_name_tab
                                st.metric(label=_( "pb_label", lang, discipline_short_name=short_disc_name_tab), value=val_tab)
                                if dt_tab: st.caption(_("achieved_on_caption", lang, date=dt_tab))
                                elif val_tab == "N/A": st.caption(_("no_record_yet_caption", lang))
                        # st.markdown("</div>", unsafe_allow_html=True) # Removed
                    st.markdown("") 
                    
                    sub_tab_titles_user = [_("disciplines." + key, lang) for key in discipline_keys]
                    sub_tabs_user = st.tabs(sub_tab_titles_user)

                    for i_sub_tab_user, disc_key_sub_tab_user in enumerate(discipline_keys):
                        with sub_tabs_user[i_sub_tab_user]:
                            sub_tab_specific_records_user_for_graph = [
                                r_sub_tab_u for r_sub_tab_u in user_records_for_tab 
                                if r_sub_tab_u['discipline'] == disc_key_sub_tab_user and r_sub_tab_u.get('parsed_value') is not None
                            ]
                            st.markdown(f"#### {_('performance_evolution_subheader', lang)}")
                            if sub_tab_specific_records_user_for_graph:
                                chart_data_list_sub_tab_user = []
                                for r_chart_sub_tab_u in sorted(sub_tab_specific_records_user_for_graph, key=lambda x_chart_u: x_chart_u['date']):
                                    chart_data_list_sub_tab_user.append({
                                        "Date": pd.to_datetime(r_chart_sub_tab_u['date']), 
                                        "PerformanceValue": r_chart_sub_tab_u['parsed_value']
                                    })
                                if chart_data_list_sub_tab_user:
                                    chart_df_sub_tab_user = pd.DataFrame(chart_data_list_sub_tab_user).set_index("Date")
                                    performance_series_name_sub_tab_user = _("disciplines." + disc_key_sub_tab_user, lang)
                                    unit_key_user_sub = 'seconds_unit' if is_time_based_discipline(disc_key_sub_tab_user) else 'meters_unit'
                                    performance_series_name_sub_tab_user += f" ({_(unit_key_user_sub, lang)})"
                                    chart_df_sub_tab_user.rename(columns={"PerformanceValue": performance_series_name_sub_tab_user}, inplace=True)
                                    st.line_chart(chart_df_sub_tab_user)
                                else: st.caption(_("no_data_for_graph", lang))
                            else: st.caption(_("no_data_for_graph", lang))
                            
                            st.markdown(f"#### {_('history_table_subheader', lang)}")
                            
                            history_for_editor_raw = [
                                r for r in user_records_for_tab if r['discipline'] == disc_key_sub_tab_user
                            ]
                            
                            if not history_for_editor_raw:
                                st.caption(_("no_history_display", lang))
                            else:
                                history_for_editor_display = []
                                for rec in sorted(history_for_editor_raw, key=lambda x: x['date'], reverse=True):
                                    history_for_editor_display.append({
                                        "id": rec.get("id"), 
                                        _("history_date_col", lang): rec.get("date"), 
                                        _("history_performance_col", lang): rec.get("original_performance_str", ""),
                                        _("history_delete_col_editor", lang): False 
                                    })
                                
                                history_df_for_editor = pd.DataFrame(history_for_editor_display)
                                
                                if not history_df_for_editor.empty:
                                    date_column_name = _("history_date_col", lang)
                                    history_df_for_editor[date_column_name] = pd.to_datetime(
                                        history_df_for_editor[date_column_name], 
                                        errors='coerce' 
                                    ).dt.date 

                                data_editor_key = f"data_editor_{current_user}_{disc_key_sub_tab_user}"
                                
                                edited_df = st.data_editor(
                                    history_df_for_editor,
                                    column_config={
                                        "id": None, 
                                        _("history_date_col", lang): st.column_config.DateColumn(
                                            label=_("history_date_col", lang),
                                            format="YYYY-MM-DD", 
                                        ),
                                        _("history_performance_col", lang): st.column_config.TextColumn(
                                            label=_("history_performance_col", lang),
                                        ),
                                        _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(
                                            label=_("history_delete_col_editor", lang),
                                            default=False,
                                        )
                                    },
                                    hide_index=True,
                                    key=data_editor_key,
                                    num_rows="dynamic" 
                                )

                                if st.button(_("save_history_changes_button", lang), key=f"save_hist_{disc_key_sub_tab_user}"):
                                    changes_made = False
                                    temp_all_records_loaded = [r.copy() for r in all_records_loaded] 

                                    processed_ids_from_editor = set()

                                    for index, edited_row_series in edited_df.iterrows():
                                        edited_row = edited_row_series.to_dict()
                                        record_id = edited_row.get("id")
                                        if record_id is None: 
                                            st.warning(f"Row {index+1} is missing an ID. Skipping.")
                                            continue
                                        
                                        processed_ids_from_editor.add(record_id)
                                        
                                        original_record_index = -1
                                        original_record = None
                                        for i, r in enumerate(temp_all_records_loaded):
                                            if r.get('id') == record_id:
                                                original_record_index = i
                                                original_record = r
                                                break
                                        
                                        if original_record is None:
                                            st.error(f"Error: Original record with ID {record_id} (from editor) not found in master list. Skipping.")
                                            continue

                                        if edited_row[_("history_delete_col_editor", lang)]: 
                                            if original_record_index != -1: 
                                                del temp_all_records_loaded[original_record_index]
                                                changes_made = True
                                            continue 

                                        edited_date_obj = edited_row[_("history_date_col", lang)]
                                        edited_date_str_to_save = None
                                        if pd.isna(edited_date_obj) or edited_date_obj is None:
                                            edited_date_str_to_save = original_record.get('date') if pd.isna(edited_date_obj) else None
                                        elif isinstance(edited_date_obj, date):
                                            edited_date_str_to_save = edited_date_obj.isoformat()
                                        else: 
                                            edited_date_str_to_save = str(edited_date_obj) 

                                        edited_perf_str = str(edited_row[_("history_performance_col", lang)])

                                        if (original_record.get('date') != edited_date_str_to_save or
                                            original_record.get('original_performance_str') != edited_perf_str):
                                            
                                            parsed_edited_value = None
                                            valid_edit_for_row = True
                                            current_record_discipline = original_record['discipline'] 

                                            if is_time_based_discipline(current_record_discipline):
                                                parsed_edited_value = parse_static_time_to_seconds(edited_perf_str, lang)
                                            else: 
                                                parsed_edited_value = parse_distance_to_meters(edited_perf_str, lang)
                                            
                                            if parsed_edited_value is None:
                                                valid_edit_for_row = False
                                                st.error(f"Invalid performance format for '{edited_perf_str}' (ID: {record_id}). Changes not saved for this row.")
                                            
                                            if valid_edit_for_row and original_record_index != -1:
                                                temp_all_records_loaded[original_record_index]['date'] = edited_date_str_to_save
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

        with tab_ranking:
            if not all_records_loaded:
                 st.info(_("no_ranking_data", lang)) 
            else:
                with st.container(border=True): # Added border
                    # st.markdown("<div style='background-color: #ffffe0; padding: 10px; border-radius: 5px; margin-bottom:15px;'>", unsafe_allow_html=True) # Removed
                    st.subheader(_("club_bests_subheader", lang))
                    club_pbs = {}
                    for disc_key_club_pb in discipline_keys:
                        club_disc_records = [
                            r for r in all_records_loaded 
                            if r['discipline'] == disc_key_club_pb and r.get('parsed_value') is not None
                        ]
                        if not club_disc_records:
                            club_pbs[disc_key_club_pb] = ("N/A", None, None)
                            continue
                        
                        if disc_key_club_pb == "16x25m Speed Endurance": 
                            best_club_record = min(club_disc_records, key=lambda x: x['parsed_value'])
                        else: 
                            best_club_record = max(club_disc_records, key=lambda x: x['parsed_value'])

                        club_pb_value_formatted = ""
                        if is_time_based_discipline(disc_key_club_pb):
                            club_pb_value_formatted = format_seconds_to_static_time(best_club_record['parsed_value'])
                        else:
                            club_pb_value_formatted = f"{best_club_record['parsed_value']}m"
                        club_pbs[disc_key_club_pb] = (club_pb_value_formatted, best_club_record['user'], best_club_record['date'])

                    cols_club_pb = st.columns(len(discipline_keys))
                    for i, disc_key_club_pb_col in enumerate(discipline_keys):
                        val_club, user_club, date_club = club_pbs.get(disc_key_club_pb_col, ("N/A", None, None))
                        with cols_club_pb[i]:
                            translated_full_disc_name_club = _("disciplines." + disc_key_club_pb_col, lang)
                            short_disc_name_club = translated_full_disc_name_club.split('(')[0].strip()
                            if not short_disc_name_club: short_disc_name_club = translated_full_disc_name_club
                            
                            st.metric(label=_("club_best_label", lang, discipline_short_name=short_disc_name_club), value=val_club)
                            if user_club and date_club:
                                st.caption(_("achieved_by_on_caption", lang, user=user_club, date=date_club))
                            elif val_club == "N/A":
                                st.caption(_("no_record_yet_caption", lang))
                    # st.markdown("</div>", unsafe_allow_html=True) # Removed
                st.markdown("") 

                ranking_sub_tab_titles = [_("disciplines." + key, lang) for key in discipline_keys]
                ranking_sub_tabs = st.tabs(ranking_sub_tab_titles)

                for i_rank_sub_tab, selected_discipline_ranking_key in enumerate(discipline_keys):
                    with ranking_sub_tabs[i_rank_sub_tab]:
                        user_pbs_for_discipline_ranking = []
                        for u_rank_tab in all_known_users_list: 
                            user_specific_discipline_records_ranking = [
                                r_rank_tab for r_rank_tab in all_records_loaded 
                                if r_rank_tab['user'] == u_rank_tab and \
                                   r_rank_tab['discipline'] == selected_discipline_ranking_key and \
                                   r_rank_tab.get('parsed_value') is not None
                            ]
                            if user_specific_discipline_records_ranking:
                                if selected_discipline_ranking_key == "16x25m Speed Endurance": 
                                    best_record_for_user_ranking = min(user_specific_discipline_records_ranking, key=lambda x_rank_tab: x_rank_tab['parsed_value'])
                                else: 
                                    best_record_for_user_ranking = max(user_specific_discipline_records_ranking, key=lambda x_rank_tab: x_rank_tab['parsed_value'])
                                
                                user_pbs_for_discipline_ranking.append({
                                    "user": u_rank_tab,
                                    "parsed_value": best_record_for_user_ranking['parsed_value'],
                                    "date": best_record_for_user_ranking['date'],
                                    "original_performance_str": best_record_for_user_ranking.get('original_performance_str')
                                })
                        
                        sort_reverse_ranking = True
                        if selected_discipline_ranking_key == "16x25m Speed Endurance":
                            sort_reverse_ranking = False 
                        
                        sorted_rankings_tab = sorted(user_pbs_for_discipline_ranking, key=lambda x_sort_tab: x_sort_tab['parsed_value'], reverse=sort_reverse_ranking)


                        if not sorted_rankings_tab:
                            st.info(_("no_ranking_data", lang))
                        else:
                            st.subheader(_("podium_header", lang))
                            podium_cols_tab = st.columns(3)
                            medal_emojis_tab = ["🥇", "🥈", "🥉"]
                            for i_podium_tab, rank_entry_tab in enumerate(sorted_rankings_tab[:3]):
                                with podium_cols_tab[i_podium_tab]:
                                    perf_display_podium_tab = ""
                                    if is_time_based_discipline(selected_discipline_ranking_key):
                                        perf_display_podium_tab = format_seconds_to_static_time(rank_entry_tab['parsed_value'])
                                    else:
                                        perf_display_podium_tab = f"{rank_entry_tab['parsed_value']}m"
                                    st.markdown(f"<div style='text-align: center; border: 2px solid #ddd; border-radius: 10px; padding: 10px; margin: 5px; background-color: #f9f9f9;'><h3>{medal_emojis_tab[i_podium_tab]} {rank_entry_tab['user']}</h3><h4>{perf_display_podium_tab}</h4><p style='font-size: 0.9em;'>{_('achieved_on_caption', lang, date=rank_entry_tab['date'])}</p></div>", unsafe_allow_html=True)
                            
                            if len(sorted_rankings_tab) < 3: 
                                for i_empty_podium_tab in range(len(sorted_rankings_tab), 3):
                                     with podium_cols_tab[i_empty_podium_tab]:
                                        st.markdown(f"<div style='text-align: center; border: 2px solid #eee; border-radius: 10px; padding: 10px; margin: 5px; opacity: 0.5;'><h3>{medal_emojis_tab[i_empty_podium_tab]}</h3><h4>-</h4><p style='font-size: 0.9em;'>&nbsp;</p></div>", unsafe_allow_html=True)

                            st.markdown("") 
                            st.subheader(_("full_ranking_header", lang))
                            ranking_table_data_tab = []
                            for rank_idx_tab, rank_item_tab in enumerate(sorted_rankings_tab):
                                perf_display_table_tab = ""
                                if is_time_based_discipline(selected_discipline_ranking_key):
                                    perf_display_table_tab = format_seconds_to_static_time(rank_item_tab['parsed_value'])
                                else:
                                    perf_display_table_tab = f"{rank_item_tab['parsed_value']}m"
                                ranking_table_data_tab.append({
                                    _("rank_col", lang): rank_idx_tab + 1,
                                    _("user_col", lang): rank_item_tab['user'],
                                    _("best_performance_col", lang): perf_display_table_tab,
                                    _("date_achieved_col", lang): rank_item_tab['date']
                                })
                            ranking_df_tab = pd.DataFrame(ranking_table_data_tab)
                            st.dataframe(ranking_df_tab, use_container_width=True, hide_index=True)

                            st.markdown("") 
                            st.subheader(_("certification_stats_header", lang))
                            
                            data_for_stats = []
                            for item_stat in user_pbs_for_discipline_ranking: 
                                user_name_stat = item_stat['user']
                                user_profile_stat = user_profiles.get(user_name_stat, {})
                                certification_stat = user_profile_stat.get("certification", _("no_certification_option", lang))
                                data_for_stats.append({
                                    "certification": certification_stat,
                                    "parsed_value": item_stat['parsed_value']
                                })
                            
                            if not data_for_stats:
                                st.info(_("no_stats_data", lang))
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
                                    if is_time_based:
                                        return format_seconds_to_static_time(value)
                                    else: 
                                        if isinstance(value, float) and not value.is_integer(): 
                                             return f"{value:.1f}m" 
                                        return f"{int(value)}m"


                                certification_summary[_("min_performance_col", lang)] = certification_summary['min_perf'].apply(lambda x: format_perf_value_for_stats(x, is_time_discipline_for_stats))
                                certification_summary[_("max_performance_col", lang)] = certification_summary['max_perf'].apply(lambda x: format_perf_value_for_stats(x, is_time_discipline_for_stats))
                                certification_summary[_("avg_performance_col", lang)] = certification_summary['avg_perf'].apply(lambda x: format_perf_value_for_stats(x, is_time_discipline_for_stats))
                                
                                display_stats_df = certification_summary[[
                                    'certification', 
                                    _("min_performance_col", lang), 
                                    _("max_performance_col", lang), 
                                    _("avg_performance_col", lang)
                                ]].rename(columns={'certification': _("certification_level_col", lang)})
                                
                                if display_stats_df.empty:
                                    st.info(_("no_stats_data", lang))
                                else:
                                    st.dataframe(display_stats_df, use_container_width=True, hide_index=True)
        
        with tab_club_perf:
            # st.header(_("club_performances_tab_title", lang)) # Removed header
            if not all_records_loaded:
                st.info(_("no_data_for_club_performance_display", lang))
            else:
                for disc_key_club in discipline_keys:
                    st.subheader(_("disciplines." + disc_key_club, lang))
                    
                    club_discipline_records = [
                        r for r in all_records_loaded 
                        if r['discipline'] == disc_key_club and r.get('parsed_value') is not None
                    ]

                    if not club_discipline_records:
                        st.caption(_("no_data_for_club_performance_display", lang))
                        continue

                    df_club_discipline = pd.DataFrame(club_discipline_records)
                    df_club_discipline['date'] = pd.to_datetime(df_club_discipline['date'])
                    
                    individual_lines = alt.Chart(df_club_discipline).mark_line(point=True).encode(
                        x=alt.X('date:T', title=_("history_date_col", lang)),
                        y=alt.Y('parsed_value:Q', title=_("performance_value", lang) + (f" ({_('seconds_unit', lang)})" if is_time_based_discipline(disc_key_club) else f" ({_('meters_unit', lang)})") ),
                        color='user:N',
                        tooltip=[
                            alt.Tooltip('user:N', title=_("user_col", lang)),
                            alt.Tooltip('date:T', title=_("history_date_col", lang)),
                            alt.Tooltip('original_performance_str:N', title=_("history_performance_col", lang))
                        ]
                    ).interactive()

                    df_club_discipline_for_avg = df_club_discipline.set_index('date')
                    quarterly_avg_df = df_club_discipline_for_avg['parsed_value'].resample('QE').mean().reset_index() 
                    quarterly_avg_df.columns = ['date', 'average_performance'] 

                    if not quarterly_avg_df.empty:
                        average_line = alt.Chart(quarterly_avg_df).mark_line(
                            color='black', 
                            strokeDash=[5,5],
                            size=2 
                        ).encode(
                            x=alt.X('date:T', title=_("history_date_col", lang)),
                            y=alt.Y('average_performance:Q', title=_("performance_value", lang)), 
                            tooltip=[
                                alt.Tooltip('date:T', title=_("history_date_col", lang), format='%Y-%m'), 
                                alt.Tooltip('average_performance:Q', title=_("quarterly_average_label", lang), format=".2f" if not is_time_based_discipline(disc_key_club) else "") 
                            ]
                        )
                        combined_chart = alt.layer(individual_lines, average_line).resolve_scale(y='shared')
                        st.altair_chart(combined_chart, use_container_width=True)
                    else:
                        st.altair_chart(individual_lines, use_container_width=True) 
                        st.caption("Not enough data for quarterly average.")
        
        with tab_divers:
            # st.header(_("divers_tab_title", lang)) # Removed header
            
            cert_order = ["I3", "I2", "I1", "A3", "A2", "A1", _("no_certification_option", lang)]
            cert_order_map = {level: i for i, level in enumerate(cert_order)}

            if not all_known_users_list:
                st.info(_("no_users_yet", lang)) 
            else:
                divers_data_for_editor = []
                for user_name in all_known_users_list:
                    profile = user_profiles.get(user_name, {})
                    certification = profile.get("certification", _("no_certification_option", lang))
                    cert_date_str = profile.get("certification_date") 
                    cert_date_obj = None
                    if cert_date_str:
                        try:
                            cert_date_obj = date.fromisoformat(cert_date_str)
                        except ValueError:
                            pass 
                    
                    lifras_id = profile.get("lifras_id", "")
                    
                    user_pbs_display = {}
                    for disc_key in discipline_keys:
                        user_disc_records = [
                            r for r in all_records_loaded 
                            if r['user'] == user_name and r['discipline'] == disc_key and r.get('parsed_value') is not None
                        ]
                        if user_disc_records:
                            if disc_key == "16x25m Speed Endurance": 
                                best_record = min(user_disc_records, key=lambda x: x['parsed_value'])
                            else: 
                                best_record = max(user_disc_records, key=lambda x: x['parsed_value'])
                            
                            if is_time_based_discipline(disc_key):
                                user_pbs_display[disc_key] = format_seconds_to_static_time(best_record['parsed_value'])
                            else:
                                user_pbs_display[disc_key] = f"{best_record['parsed_value']}m"
                        else:
                            user_pbs_display[disc_key] = "N/A"

                    divers_data_for_editor.append({
                        _("original_name_col_editor_hidden", lang): user_name, 
                        _("diver_name_col_editor", lang): user_name,
                        _("certification_col_editor", lang): certification,
                        _("certification_date_col_editor", lang): cert_date_obj, 
                        _("lifras_id_col_editor", lang): lifras_id,
                        _("pb_sta_col_editor", lang): user_pbs_display.get("Static Apnea (STA)", "N/A"),
                        _("pb_dynbf_col_editor", lang): user_pbs_display.get("Dynamic Bi-fins (DYN-BF)", "N/A"),
                        _("pb_depth_col_editor", lang): user_pbs_display.get("Depth (CWT/FIM)", "N/A"),
                        _("pb_16x25_col_editor", lang): user_pbs_display.get("16x25m Speed Endurance", "N/A"),
                    })
                
                def sort_divers(diver_entry):
                    cert_level = diver_entry[_("certification_col_editor", lang)]
                    cert_date_val = diver_entry[_("certification_date_col_editor", lang)]
                    sortable_cert_date = cert_date_val if cert_date_val is not None else date.min 
                    return (cert_order_map.get(cert_level, len(cert_order)), sortable_cert_date)

                sorted_divers_data = sorted(divers_data_for_editor, key=sort_divers)
                divers_df = pd.DataFrame(sorted_divers_data)


                cert_options_for_editor = [_("no_certification_option", lang)] + list(_("certification_levels", lang).keys())
                
                column_config_divers = {
                    _("original_name_col_editor_hidden", lang): None, 
                    _("diver_name_col_editor", lang): st.column_config.TextColumn(
                        label=_("diver_name_col_editor", lang),
                        required=True,
                    ),
                    _("certification_col_editor", lang): st.column_config.SelectboxColumn(
                        label=_("certification_col_editor", lang),
                        options=cert_options_for_editor,
                        required=False, 
                    ),
                    _("certification_date_col_editor", lang): st.column_config.DateColumn(
                        label=_("certification_date_col_editor", lang),
                        format="YYYY-MM-DD",
                    ),
                    _("lifras_id_col_editor", lang): st.column_config.TextColumn(
                        label=_("lifras_id_col_editor", lang),
                    ),
                    _("pb_sta_col_editor", lang): st.column_config.TextColumn(label=_("pb_sta_col_editor", lang), disabled=True),
                    _("pb_dynbf_col_editor", lang): st.column_config.TextColumn(label=_("pb_dynbf_col_editor", lang), disabled=True),
                    _("pb_depth_col_editor", lang): st.column_config.TextColumn(label=_("pb_depth_col_editor", lang), disabled=True),
                    _("pb_16x25_col_editor", lang): st.column_config.TextColumn(label=_("pb_16x25_col_editor", lang), disabled=True),
                }


                edited_divers_df = st.data_editor(
                    divers_df,
                    column_config=column_config_divers,
                    key="divers_data_editor",
                    num_rows="fixed", 
                    hide_index=True
                )

                if st.button(_("save_divers_changes_button", lang), key="save_divers_changes"):
                    changes_made_divers = False
                    temp_user_profiles = user_profiles.copy() 
                    temp_all_records = [r.copy() for r in all_records_loaded] 

                    for index, edited_row in edited_divers_df.iterrows():
                        original_name = edited_row[_("original_name_col_editor_hidden", lang)]
                        new_name = edited_row[_("diver_name_col_editor", lang)].strip()
                        new_certification = edited_row[_("certification_col_editor", lang)]
                        new_cert_date_obj = edited_row[_("certification_date_col_editor", lang)]
                        new_cert_date_str = new_cert_date_obj.isoformat() if isinstance(new_cert_date_obj, date) else None
                        new_lifras_id = edited_row[_("lifras_id_col_editor", lang)].strip()


                        if not new_name:
                            st.error(f"Diver name cannot be empty (row {index + 1}).")
                            continue 

                        other_original_names = [
                            name for name in all_known_users_list if name != original_name
                        ]
                        if new_name != original_name and new_name in other_original_names:
                            st.error(_("name_conflict_error", lang, new_name=new_name))
                            continue 

                        profile_data_to_update = temp_user_profiles.get(original_name, {})
                        
                        name_changed = original_name != new_name
                        cert_changed = profile_data_to_update.get("certification") != new_certification
                        cert_date_changed = profile_data_to_update.get("certification_date") != new_cert_date_str
                        lifras_id_changed = profile_data_to_update.get("lifras_id", "") != new_lifras_id

                        if name_changed or cert_changed or cert_date_changed or lifras_id_changed:
                            changes_made_divers = True
                            if name_changed:
                                old_profile_data = temp_user_profiles.pop(original_name, {"certification": _("no_certification_option", lang), "certification_date": None, "lifras_id": ""})
                                old_profile_data['certification'] = new_certification 
                                old_profile_data['certification_date'] = new_cert_date_str
                                old_profile_data['lifras_id'] = new_lifras_id
                                temp_user_profiles[new_name] = old_profile_data
                                
                                for record in temp_all_records:
                                    if record['user'] == original_name:
                                        record['user'] = new_name
                            
                                if st.session_state.get('current_user') == original_name:
                                    st.session_state.current_user = new_name
                                    st.session_state.current_user_sidebar_selection = new_name
                            else: 
                                temp_user_profiles.setdefault(original_name, {})
                                temp_user_profiles[original_name]['certification'] = new_certification
                                temp_user_profiles[original_name]['certification_date'] = new_cert_date_str
                                temp_user_profiles[original_name]['lifras_id'] = new_lifras_id
                        

                    if changes_made_divers:
                        user_profiles.clear()
                        user_profiles.update(temp_user_profiles)
                        all_records_loaded[:] = temp_all_records

                        save_user_profiles(user_profiles)
                        save_records(all_records_loaded)
                        st.success(_("divers_updated_success", lang))
                        st.rerun()
                    else:
                        st.info("No changes detected in diver data.")
                
                st.markdown("---")
                st.subheader(_("certification_summary_header", lang))
                
                cert_counts = {}
                for profile in user_profiles.values():
                    cert_level = profile.get("certification", _("no_certification_option", lang))
                    cert_counts[cert_level] = cert_counts.get(cert_level, 0) + 1
                
                if not cert_counts:
                    st.info(_("no_stats_data", lang)) 
                else:
                    summary_data = [{_("certification_level_col", lang): level, _("count_col", lang): count} for level, count in cert_counts.items()]
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
        
        with tab_training:
            # st.header(_("training_log_tab_title", lang)) # Removed header
            if not training_log_loaded:
                st.info("No training sessions logged yet.") 
            else:
                training_log_display = []
                for entry in sorted(training_log_loaded, key=lambda x: x['date'], reverse=True):
                    training_log_display.append({
                        "id": entry.get("id"),
                        _("training_date_label", lang): entry.get("date"),
                        _("training_place_label", lang): entry.get("place"),
                        _("training_description_label", lang): entry.get("description"),
                        _("history_delete_col_editor", lang): False 
                    })
                
                training_df_for_editor = pd.DataFrame(training_log_display)
                if not training_df_for_editor.empty:
                    training_date_col_name = _("training_date_label", lang)
                    training_df_for_editor[training_date_col_name] = pd.to_datetime(
                        training_df_for_editor[training_date_col_name],
                        errors='coerce'
                    ).dt.date

                edited_training_df = st.data_editor(
                    training_df_for_editor,
                    column_config={
                        "id": None, 
                        _("training_date_label", lang): st.column_config.DateColumn(
                            label=_("training_date_label", lang), format="YYYY-MM-DD"
                        ),
                        _("training_place_label", lang): st.column_config.TextColumn(
                            label=_("training_place_label", lang)
                        ),
                        _("training_description_label", lang): st.column_config.TextColumn(
                            label=_("training_description_label", lang)
                        ),
                        _("history_delete_col_editor", lang): st.column_config.CheckboxColumn(
                            label=_("history_delete_col_editor", lang), default=False
                        )
                    },
                    hide_index=True,
                    key="training_log_editor",
                    num_rows="dynamic"
                )

                if st.button(_("save_training_log_changes_button", lang), key="save_training_log_changes"):
                    training_changes_made = False
                    temp_training_log_loaded = [log.copy() for log in training_log_loaded]

                    for index, edited_row_series in edited_training_df.iterrows():
                        edited_row = edited_row_series.to_dict()
                        log_id = edited_row.get("id")
                        if log_id is None: continue

                        original_log_index = -1
                        for i, log_item in enumerate(temp_training_log_loaded):
                            if log_item.get("id") == log_id:
                                original_log_index = i
                                break
                        
                        if original_log_index == -1: continue 

                        if edited_row[_("history_delete_col_editor", lang)]:
                            del temp_training_log_loaded[original_log_index]
                            training_changes_made = True
                            continue
                        
                        edited_log_date_obj = edited_row[_("training_date_label", lang)]
                        edited_log_date_str = edited_log_date_obj.isoformat() if isinstance(edited_log_date_obj, date) else str(edited_log_date_obj)
                        
                        if (temp_training_log_loaded[original_log_index]['date'] != edited_log_date_str or
                            temp_training_log_loaded[original_log_index]['place'] != edited_row[_("training_place_label", lang)] or
                            temp_training_log_loaded[original_log_index]['description'] != edited_row[_("training_description_label", lang)]):
                            
                            temp_training_log_loaded[original_log_index]['date'] = edited_log_date_str
                            temp_training_log_loaded[original_log_index]['place'] = edited_row[_("training_place_label", lang)]
                            temp_training_log_loaded[original_log_index]['description'] = edited_row[_("training_description_label", lang)]
                            training_changes_made = True
                    
                    if training_changes_made:
                        training_log_loaded[:] = temp_training_log_loaded
                        save_training_log(training_log_loaded)
                        st.success(_("training_log_updated_success", lang))
                        st.rerun()
                    else:
                        st.info("No changes detected in the training log.")


if __name__ == "__main__":
    main()
