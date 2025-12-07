import hashlib
import base64
from django.conf import settings

try:
    import firebase_admin
    from firebase_admin import credentials, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class FirebaseStorageService:
    """
    Servicio para almacenar firmas en Firebase Storage
    Si Firebase no está configurado, guarda localmente
    """
    
    def __init__(self):
        self.firebase_enabled = FIREBASE_AVAILABLE and settings.FIREBASE_CREDENTIALS_PATH
        if self.firebase_enabled and not firebase_admin._apps:
            try:
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': settings.FIREBASE_STORAGE_BUCKET
                })
            except Exception as e:
                print(f"Error inicializando Firebase: {e}")
                self.firebase_enabled = False
    
    def save_signature(self, user_id, charla_id, signature_data):
        """
        Guarda la firma y retorna un hash único
        
        Args:
            user_id: ID del usuario
            charla_id: ID de la charla
            signature_data: Datos de la firma (base64 o string)
        
        Returns:
            str: Hash único de la firma
        """
        # Generar hash único
        firma_hash = hashlib.sha256(
            f"{user_id}-{charla_id}-{signature_data}".encode()
        ).hexdigest()
        
        if self.firebase_enabled:
            try:
                # Guardar en Firebase Storage
                bucket = storage.bucket()
                blob = bucket.blob(f'firmas/{user_id}/{charla_id}.png')
                
                # Convertir base64 a bytes si es necesario
                if signature_data.startswith('data:image'):
                    signature_data = signature_data.split(',')[1]
                
                image_data = base64.b64decode(signature_data)
                blob.upload_from_string(image_data, content_type='image/png')
                
                print(f"Firma guardada en Firebase: firmas/{user_id}/{charla_id}.png")
            except Exception as e:
                print(f"Error guardando en Firebase: {e}")
                self._save_local(user_id, charla_id, signature_data)
        else:
            self._save_local(user_id, charla_id, signature_data)
        
        return firma_hash
    
    def _save_local(self, user_id, charla_id, signature_data):
        """Guarda la firma localmente como fallback"""
        import os
        from django.conf import settings
        
        # Crear directorio si no existe
        firma_dir = os.path.join(settings.MEDIA_ROOT, 'firmas', str(user_id))
        os.makedirs(firma_dir, exist_ok=True)
        
        # Guardar archivo
        file_path = os.path.join(firma_dir, f'{charla_id}.png')
        
        try:
            if signature_data.startswith('data:image'):
                signature_data = signature_data.split(',')[1]
            
            image_data = base64.b64decode(signature_data)
            with open(file_path, 'wb') as f:
                f.write(image_data)
            print(f"Firma guardada localmente: {file_path}")
        except Exception as e:
            print(f"Error guardando localmente: {e}")
    
    def get_signature_url(self, user_id, charla_id):
        """Obtiene la URL de la firma (Firebase o local)"""
        if self.firebase_enabled:
            try:
                bucket = storage.bucket()
                blob = bucket.blob(f'firmas/{user_id}/{charla_id}.png')
                return blob.public_url
            except:
                pass
        
        # URL local
        return f"{settings.MEDIA_URL}firmas/{user_id}/{charla_id}.png"