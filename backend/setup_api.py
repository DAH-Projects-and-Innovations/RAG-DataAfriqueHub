from src import quick_start

try:
    # On tente de lancer le moteur avec ton fichier de config
    pipeline = quick_start('configs/hybrid.yaml')
    
    # On pose une question
    response = pipeline.query("Qui est l'auteur du projet ?")
    
    print("\n--- RÉSULTAT DU TEST ---")
    print(f"Réponse reçue : {response.answer}")
    print("------------------------")
    print("✅ Si tu vois une réponse 'Stub', l'intégration est parfaite !")
except Exception as e:
    print(f"❌ Erreur d'intégration : {e}")