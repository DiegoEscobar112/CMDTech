import React, { useState } from 'react';
import { IonPage, IonHeader, IonToolbar, IonTitle, IonContent, IonItem, IonLabel, IonInput, IonButton } from '@ionic/react';

const Register: React.FC = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');

  const handlePhoneChange = (e: CustomEvent) => {
    const value = e.detail.value!;
    if (/^\d*$/.test(value)) {
      setPhone(value);
    }
  };

  const handleRegister = () => {
    // Aquí podrías manejar la lógica de registro del usuario, como llamar a una API
    console.log('Registro de usuario:', { username, email, password, phone: `+56${phone}` });
  };

  return (
    <IonPage style={{ backgroundColor: '#f0f0f0' }}>
      <IonHeader>
        <IonToolbar color="primary">
          <IonTitle>Registrar Usuario</IonTitle>
        </IonToolbar>
      </IonHeader>
      <IonContent className="ion-padding" style={{ backgroundColor: '#f0f0f0' }}>
        {/* Campo para el nombre de usuario */}
        <IonItem>
          <IonLabel position="stacked">Nombre de Usuario</IonLabel>
          <IonInput value={username} onIonChange={e => setUsername(e.detail.value!)} clearInput />
        </IonItem>

        {/* Campo para el correo electrónico */}
        <IonItem>
          <IonLabel position="stacked">Correo Electrónico</IonLabel>
          <IonInput type="email" value={email} onIonChange={e => setEmail(e.detail.value!)} clearInput />
        </IonItem>

        {/* Campo para el número de teléfono */}
        <IonItem>
          <IonLabel position="stacked">Número de Teléfono</IonLabel>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <span style={{ marginRight: '8px', fontSize: '16px' }}>+56</span>
            <IonInput
              value={phone}
              onIonChange={handlePhoneChange}
              clearInput
              type="tel"
              placeholder="912345678"
            />
          </div>
        </IonItem>

        {/* Campo para la contraseña */}
        <IonItem>
          <IonLabel position="stacked">Contraseña</IonLabel>
          <IonInput type="password" value={password} onIonChange={e => setPassword(e.detail.value!)} clearInput />
        </IonItem>

        {/* Botón para registrar */}
        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <IonButton expand="block" color="primary" onClick={handleRegister}>Registrar</IonButton>
        </div>

        {/* Botón para volver */}
        <div style={{ marginTop: '10px', textAlign: 'center' }}>
          <IonButton expand="block" color="medium" onClick={() => window.history.back()}>Volver</IonButton>
        </div>
      </IonContent>
    </IonPage>
  );
};

export default Register;
