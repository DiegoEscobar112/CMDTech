import React, { useState } from 'react';
import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonButton, IonInput, IonItem, IonLabel, IonModal, useIonRouter, IonCard, IonCardContent, IonGrid, IonRow, IonCol, IonIcon, IonToast, IonBadge, IonChip, IonSpinner } from '@ionic/react';
import { pawOutline, logInOutline, personAddOutline, cameraOutline } from 'ionicons/icons';
import axios from 'axios';

const Tab1: React.FC = () => {
  const router = useIonRouter();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showToast, setShowToast] = useState({ show: false, message: '', color: '' });
  const [profile, setProfile] = useState<{ username: string; alerts: { title: string; date: string }[]; profileImage?: string } | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = () => {
    setShowLoginModal(true);
  };

  const handleRegister = () => {
    router.push('/register');
  };

  const handleLoginSubmit = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/login', {
        username,
        password,
      });
      if (response.status === 200) {
        setShowToast({ show: true, message: 'Inicio de sesión exitoso', color: 'success' });
        setShowLoginModal(false);
        fetchUserProfile(username);
        router.push(`/profile/${username}`);
      }
    } catch (error) {
      setShowToast({ show: true, message: 'Error al iniciar sesión. Verifique sus credenciales.', color: 'danger' });
    } finally {
      setLoading(false);
    }
  };

  const fetchUserProfile = async (username: string) => {
    try {
      const response = await axios.get(`http://localhost:5000/api/profile/${username}`);
      if (response.status === 200) {
        setProfile(response.data);
      }
    } catch (error) {
      console.error('Error al obtener el perfil del usuario', error);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleUploadProfileImage = async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('profileImage', selectedFile);
    formData.append('username', username);

    try {
      const response = await axios.post('http://localhost:5000/api/uploadProfileImage', formData);
      if (response.status === 200) {
        setShowToast({ show: true, message: 'Imagen de perfil actualizada', color: 'success' });
        fetchUserProfile(username);
      }
    } catch (error) {
      setShowToast({ show: true, message: 'Error al cargar la imagen de perfil.', color: 'danger' });
    }
  };

  return (
    <IonPage style={{ backgroundColor: '#f8f9fa' }}>
      <IonHeader>
        <IonToolbar color="primary">
          <IonTitle>Finder</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding" style={{ backgroundColor: '#f8f9fa', position: 'relative' }}>
        {/* Imagen de fondo */}
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundImage: 'url(/images/gastimati.jpeg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          opacity: 0.3,
          zIndex: -1,
        }}></div>

       

        {/* Botones de Iniciar Sesión, Registro y Ver Perfil */}
        <IonGrid>
          <IonRow>
            <IonCol>
              <IonButton expand="block" color="primary" onClick={handleLogin} shape="round">
                <IonIcon slot="start" icon={logInOutline} />
                Iniciar Sesión
              </IonButton>
            </IonCol>
            <IonCol>
              <IonButton expand="block" color="secondary" onClick={handleRegister} shape="round">
                <IonIcon slot="start" icon={personAddOutline} />
                Registrar Usuario
              </IonButton>
            </IonCol>
            <IonCol>
              <IonButton expand="block" color="tertiary" onClick={() => router.push('/profile/demoUser')} shape="round">
                Ver Perfil de Prueba
              </IonButton>
            </IonCol>
          </IonRow>
        </IonGrid>

        {/* Modal de Iniciar Sesión */}
        <IonModal isOpen={showLoginModal} onDidDismiss={() => setShowLoginModal(false)}>
          <IonHeader>
            <IonToolbar color="secondary">
              <IonTitle>Iniciar Sesión</IonTitle>
            </IonToolbar>
          </IonHeader>
          <IonContent className="ion-padding" style={{ backgroundColor: '#f8f9fa' }}>
            <IonCard style={{ backgroundColor: '#ffffffee', borderRadius: '15px', margin: '20px' }}>
              <IonCardContent>
                <IonItem>
                  <IonLabel position="stacked">Nombre de Usuario</IonLabel>
                  <IonInput value={username} onIonChange={e => setUsername(e.detail.value!)} placeholder="Ingresa tu nombre de usuario" clearInput></IonInput>
                </IonItem>
                <IonItem>
                  <IonLabel position="stacked">Contraseña</IonLabel>
                  <IonInput type="password" value={password} onIonChange={e => setPassword(e.detail.value!)} placeholder="Ingresa tu contraseña" clearInput></IonInput>
                </IonItem>
                <IonGrid>
                  <IonRow>
                    <IonCol>
                      <IonButton expand="block" color="primary" onClick={handleLoginSubmit} shape="round">
                        {loading ? <IonSpinner name="dots" /> : 'Ingresar'}
                      </IonButton>
                    </IonCol>
                    <IonCol>
                      <IonButton expand="block" color="medium" onClick={() => setShowLoginModal(false)} shape="round">Cancelar</IonButton>
                    </IonCol>
                  </IonRow>
                </IonGrid>
              </IonCardContent>
            </IonCard>
          </IonContent>
        </IonModal>

        {/* Toast de mensajes */}
        <IonToast
          isOpen={showToast.show}
          message={showToast.message}
          duration={2000}
          color={showToast.color}
          onDidDismiss={() => setShowToast({ show: false, message: '', color: '' })}
        />
      </IonContent>
       {/* Descripción de la empresa */}
       <IonCard style={{ backgroundColor: '#ffffffee', borderRadius: '15px', margin: '20px' }}>
          <IonCardContent>
            <IonGrid>
              <IonRow className="ion-align-items-center">
                <IonCol size="2">
                  <IonIcon icon={pawOutline} size="large" color="primary" />
                </IonCol>
                <IonCol size="10">
                  <IonChip color="primary">
                    <IonLabel>Finder: Encuentra a tu mascota perdida</IonLabel>
                  </IonChip>
                  <p><strong>Finder</strong> es una plataforma para reportar y encontrar mascotas perdidas. Los usuarios pueden interactuar en publicaciones y utilizar tecnología de comparación de imágenes para facilitar la búsqueda.</p>
                </IonCol>
              </IonRow>
            </IonGrid>
          </IonCardContent>
        </IonCard>
    </IonPage>
  );
};

export default Tab1;
