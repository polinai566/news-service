import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './RegistrationSuccessPage.css';

function RegistrationSuccessPage() {
    const navigate = useNavigate();
    const location = useLocation();
    const login = location.state?.login || 'login';

    const [showCute, setShowCute] = useState(false);

    return (
        <div className="success-container">
            <div className="success-card">
                <div className="success-icon">✓</div>

                <h1>Регистрация завершена успешно!</h1>

                <p className="success-text">
                    Пользователь <strong>"{login}"</strong> успешно добавлен в систему
                </p>

                <div className="button-group">
                    <button
                        className="btn primary"
                        onClick={() => navigate('/signup')}
                    >
                        Регистрация
                    </button>

                    <button
                        className="btn secondary"
                        onClick={() => setShowCute(!showCute)}
                    >
                        Милые картинки
                    </button>
                </div>

                {showCute && (
                    <div className="cute-image-wrapper">
                        <img
                            src="https://images.unsplash.com/photo-1518791841217-8f162f1e1131?auto=format&fit=crop&w=900&q=60"
                            alt="Милая картинка"
                        />
                    </div>
                )}
            </div>
        </div>
    );
}

export default RegistrationSuccessPage;
