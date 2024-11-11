import React, { useEffect, useRef } from 'react';
import { IonContent, IonHeader, IonPage, IonTitle, IonToolbar, IonCard, IonCardContent, IonMenu, IonList, IonItem, IonLabel, IonIcon, IonButtons, IonMenuButton, IonFab, IonFabButton, IonFabList } from '@ionic/react';
import { locateOutline, settingsOutline, heartOutline, personCircleOutline, logOutOutline, mapOutline } from 'ionicons/icons';

const Tab2: React.FC = () => {
  const mapRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const google = (window as any).google; // Acceder a la API de Google Maps desde la ventana
    if (google && mapRef.current) {
      const map = new google.maps.Map(mapRef.current, {
        center: { lat: -33.4489, lng: -70.6693 }, // Centro del mapa (Santiago, Chile)
        zoom: 13,
      });

      // Agregar marcador
      new google.maps.Marker({
        position: { lat: -33.4489, lng: -70.6693 },
        map,
      });
    }
  }, []);

  return (
    <>
      {/* Menú lateral */}
      <IonMenu contentId="main-content">
        <IonHeader>
          <IonToolbar color="primary">
            <IonTitle>Menú</IonTitle>
          </IonToolbar>
        </IonHeader>
        <IonContent>
          <IonList>
            <IonItem button>
              <IonIcon icon={personCircleOutline} slot="start" />
              <IonLabel>Perfil</IonLabel>
            </IonItem>
            <IonItem button>
              <IonIcon icon={settingsOutline} slot="start" />
              <IonLabel>Configuración</IonLabel>
            </IonItem>
            <IonItem button>
              <IonIcon icon={heartOutline} slot="start" />
              <IonLabel>Favoritos</IonLabel>
            </IonItem>
            <IonItem button>
              <IonIcon icon={logOutOutline} slot="start" />
              <IonLabel>Salir</IonLabel>
            </IonItem>
          </IonList>
        </IonContent>
      </IonMenu>

      <IonPage id="main-content">
        <IonHeader>
          <IonToolbar color="primary">
            <IonButtons slot="start">
              <IonMenuButton />
            </IonButtons>
            <IonTitle>Inicio</IonTitle>
          </IonToolbar>
        </IonHeader>
        <IonContent>
          {/* Tarjeta del mapa */}
          <IonCard style={{ margin: '20px' }}>
            <IonCardContent>
              <div ref={mapRef} style={{ width: '100%', height: '450px' }}></div>
            </IonCardContent>
          </IonCard>

          {/* Botón flotante para acciones rápidas */}
          <IonFab vertical="bottom" horizontal="end" slot="fixed">
            <IonFabButton color="primary">
              <IonIcon icon={mapOutline} />
            </IonFabButton>
            <IonFabList side="top">
              <IonFabButton color="secondary">
                <IonIcon icon={locateOutline} />
              </IonFabButton>
              <IonFabButton color="secondary">
                <IonIcon icon={heartOutline} />
              </IonFabButton>
            </IonFabList>
          </IonFab>
        </IonContent>
      </IonPage>
    </>
  );
};

export default Tab2;
