import React, { useEffect, useState } from 'react';
import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonCard, IonCardContent, IonItem, IonLabel, IonInput, IonList, IonButton, IonAvatar, IonIcon, IonRow, IonCol, IonToast } from '@ionic/react';
import { cameraOutline, saveOutline, createOutline } from 'ionicons/icons';
import axios from 'axios';

interface Alert {
  title: string;
  date: string;
}

interface UserProfileProps {
  username: string;
}

const UserProfile: React.FC<UserProfileProps> = ({ username }) => {
  const [userName, setUserName] = useState(username);
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [profileImage, setProfileImage] = useState<File | null>(null);
  const [profileImageUrl, setProfileImageUrl] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [showToast, setShowToast] = useState({ show: false, message: '', color: '' });

  useEffect(() => {
    // Aquí se debe hacer la llamada a la API para obtener los datos del perfil del usuario
    const fetchUserProfile = async () => {
      try {
        const response = await axios.get(`http://localhost:5000/api/profile/${username}`);
        if (response.status === 200) {
          const { email, phone, alerts, profileImageUrl } = response.data;
          setEmail(email);
          setPhone(phone);
          setAlerts(alerts);
          if (profileImageUrl) {
            setProfileImageUrl(profileImageUrl);
          }
        }
      } catch (error) {
        console.error('Error al obtener el perfil del usuario', error);
      }
    };

    fetchUserProfile();
  }, [username]);

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setProfileImage(event.target.files[0]);
    }
  };

  const handleUploadImage = async () => {
    if (profileImage) {
      const formData = new FormData();
      formData.append('profileImage', profileImage);
      try {
        const response = await axios.post(`http://localhost:5000/api/profile/${username}/upload`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        if (response.status === 200) {
          setProfileImageUrl(URL.createObjectURL(profileImage));
          setShowToast({ show: true, message: 'Imagen subida exitosamente', color: 'success' });
        }
      } catch (error) {
        console.error('Error al subir la imagen', error);
      }
    }
  };

  const handleSaveProfile = async () => {
    try {
      const response = await axios.put(`http://localhost:5000/api/profile/${username}`, {
        userName,
        email,
        phone,
      });
      if (response.status === 200) {
        setShowToast({ show: true, message: 'Perfil actualizado exitosamente', color: 'success' });
        setIsEditing(false);
      }
    } catch (error) {
      setShowToast({ show: true, message: 'Error al actualizar el perfil', color: 'danger' });
    }
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar color="primary">
          <IonTitle>Perfil de Usuario</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding">
        <IonCard>
          <IonCardContent>
            <IonRow className="ion-align-items-center ion-justify-content-center">
              <IonAvatar style={{ width: '150px', height: '150px' }}>
                {profileImageUrl ? (
                  <img src={profileImageUrl} alt="Foto de perfil" />
                ) : (
                  <IonIcon icon={cameraOutline} style={{ fontSize: '80px', paddingTop: '30px', color: '#888' }} />
                )}
              </IonAvatar>
              <input type="file" accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} id="upload-input" />
              <IonButton
                fill="clear"
                color="secondary"
                onClick={() => document.getElementById('upload-input')?.click()}
              >
                Cambiar Foto de Perfil
              </IonButton>
            </IonRow>
            <IonButton
              expand="block"
              color="primary"
              onClick={handleUploadImage}
              disabled={!profileImage}
              style={{ marginTop: '10px' }}
            >
              Subir Imagen de Perfil
            </IonButton>
          </IonCardContent>
        </IonCard>

        <IonCard>
          <IonCardContent>
            <IonList>
              <IonItem>
                <IonLabel position="stacked"><strong>Nombre de Usuario:</strong></IonLabel>
                <IonInput
                  value={userName}
                  onIonChange={e => setUserName(e.detail.value!)}
                  readonly={!isEditing}
                />
              </IonItem>
              <IonItem>
                <IonLabel position="stacked"><strong>Correo Electrónico:</strong></IonLabel>
                <IonInput
                  value={email}
                  onIonChange={e => setEmail(e.detail.value!)}
                  readonly={!isEditing}
                />
              </IonItem>
              <IonItem>
                <IonLabel position="stacked"><strong>Número de Teléfono:</strong></IonLabel>
                <IonInput
                  type="tel"
                  value={`+56 ${phone}`}
                  onIonChange={e => setPhone(e.detail.value!.replace(/\D/g, '').slice(2))}
                  readonly={!isEditing}
                />
              </IonItem>
            </IonList>
            <IonRow className="ion-justify-content-center">
              {!isEditing ? (
                <IonButton color="secondary" onClick={() => setIsEditing(true)}>
                  <IonIcon slot="start" icon={createOutline} />
                  Editar Perfil
                </IonButton>
              ) : (
                <IonButton color="success" onClick={handleSaveProfile}>
                  <IonIcon slot="start" icon={saveOutline} />
                  Guardar Cambios
                </IonButton>
              )}
            </IonRow>
          </IonCardContent>
        </IonCard>

        <IonCard>
          <IonCardContent>
            <h2>Mis Alertas</h2>
            {alerts.length > 0 ? (
              <IonList>
                {alerts.map((alert, index) => (
                  <IonItem key={index}>
                    <IonLabel>
                      <h3>{alert.title}</h3>
                      <p>{alert.date}</p>
                    </IonLabel>
                  </IonItem>
                ))}
              </IonList>
            ) : (
              <p>No hay alertas registradas.</p>
            )}
          </IonCardContent>
        </IonCard>

        {/* Botón para volver */}
        <IonRow className="ion-justify-content-center">
          <IonCol size="6">
            <IonButton expand="block" color="primary" onClick={() => window.history.back()}>
              Volver
            </IonButton>
          </IonCol>
        </IonRow>

        {/* Toast de mensajes */}
        <IonToast
          isOpen={showToast.show}
          message={showToast.message}
          duration={2000}
          color={showToast.color}
          onDidDismiss={() => setShowToast({ show: false, message: '', color: '' })}
        />
      </IonContent>
    </IonPage>
  );
};

export default UserProfile;
