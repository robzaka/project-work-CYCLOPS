from flask import Flask, request, render_template, redirect, url_for, session
from PIL import Image
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import os
from authlib.integrations.flask_client import OAuth
from decorators import allowed_users_only

# ===================
# Configurazione Flask
# ===================
app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Cambia in qualcosa di sicuro

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ===================
# Configurazione OAuth Keycloak
# ===================
oauth = OAuth(app)
keycloak = oauth.register(
    name='keycloak',
    client_id='app2',
    client_secret='WD0ItrMAETvdXzoUPZ5heOoDWs8B7qmO',
    server_metadata_url='http://keycloak:8080/realms/myrealm/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
)

# ===================
# Modello PyTorch
# ===================
class SimpleNet(nn.Module):
    def __init__(self):
        super(SimpleNet, self).__init__()
        self.fc1 = nn.Linear(3 * 32 * 32, 128)
        self.fc2 = nn.Linear(128, 2)

    def forward(self, x):
        x = x.view(-1, 3 * 32 * 32)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Carica il modello
model = SimpleNet()
model.load_state_dict(torch.load('bird_frog_classifier.pth', map_location=torch.device('cpu')))
model.eval()

# Trasformazioni
transform = transforms.Compose([
    transforms.Resize((32, 32)),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# Classi e traduzioni
classes = ['bird', 'frog']
translations = {
    'bird': 'uccello',
    'frog': 'rana'
}

# ===================
# Autenticazione Keycloak
# ===================
@app.route('/login')
def login():
    redirect_uri = url_for('auth', _external=True)
    # Salva il nonce nella sessione
    return keycloak.authorize_redirect(redirect_uri)

@app.route('/auth')
def auth():
    token = keycloak.authorize_access_token()
    session['id_token'] = token.get('id_token')  # <--- Salviamo qui
    user_info = keycloak.parse_id_token(token, nonce=token.get("nonce"))
    session['user'] = user_info
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    id_token = session.get('id_token')
    session.clear()

    end_session_endpoint = keycloak.load_server_metadata().get("end_session_endpoint")
    post_logout_redirect_uri = url_for('index', _external=True)

    if id_token:
        return redirect(
            f"{end_session_endpoint}?post_logout_redirect_uri={post_logout_redirect_uri}&id_token_hint={id_token}"
        )
    else:
        # Se non abbiamo id_token, redirigiamo comunque alla home
        return redirect(post_logout_redirect_uri)
    
# ===================
# Rotta principale con protezione login
# ===================

@app.route('/', methods=['GET', 'POST'])
@allowed_users_only(['user1', 'user2'])  # Solo questi due possono accedere
def index():
    if 'user' not in session:
        return redirect(url_for('login'))

    prediction = None
    filename = None

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            image = Image.open(filepath).convert('RGB')
            image = transform(image).unsqueeze(0)

            with torch.no_grad():
                output = model(image)
                _, pred = torch.max(output, 1)
                prediction_en = classes[pred.item()]
                prediction = translations[prediction_en]

    return render_template('birdfrog.html', prediction=prediction, filename=filename, user=session['user'])

@app.errorhandler(403)
def forbidden(e):
    return render_template("birdfrog.html", error_code=403), 403

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)