import React, { useEffect, useState } from 'react';
import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonCard, IonCardHeader, IonCardTitle, IonCardContent } from '@ionic/react';
import axios from 'axios';

const Profile: React.FC = () => {
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        // Aquí deberías obtener el nombre de usuario de algún lugar como el estado de autenticación
        const username = 'ejemploUsuario';
        const response = await axios.get(`http://localhost:5000/api/profile/${username}`);
        setProfile(response.data);
      } catch (error) {
        console.error('Error al obtener el perfil:', error);
      }
    };

    fetchProfile();
  }, []);

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Perfil de Usuario</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding">
        {profile ? (
          <IonCard>
            <IonCardHeader>
              <IonCardTitle>Bienvenido, {profile.user.username}</IonCardTitle>
            </IonCardHeader>
            <IonCardContent>
              <h2>Alertas/Publicaciones:</h2>
              {profile.alerts.length > 0 ? (
                <ul>
                  {profile.alerts.map((alert: any, index: number) => (
                    <li key={index}>{alert}</li>
                  ))}
                </ul>
              ) : (
                <p>No hay alertas o publicaciones aún.</p>
              )}
            </IonCardContent>
          </IonCard>
        ) : (
          <p>Cargando perfil...</p>
        )}
      </IonContent>
    </IonPage>
  );
};

export default Profile;
