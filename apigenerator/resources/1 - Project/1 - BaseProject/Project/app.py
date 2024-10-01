# Infra Imports #
from src.e_Infra.g_Environment.EnvironmentVariables import *

# Controller Imports #
from src.a_Presentation.d_Swagger.SwaggerController import *
from src.a_Presentation.f_Redoc.RedocController import *
from src.a_Presentation.b_Custom.FlaskAdminPanelController import *
from src.a_Presentation.b_Custom.OptionsController import *
from src.a_Presentation.b_Custom.SQLController import *
from src.a_Presentation.b_Custom.BeforeRequestController import *
from src.a_Presentation.b_Custom.ExceptionHandlerController import *


# LocalHost run #
if __name__ == "__main__":
    app_handler.run(debug=True, use_reloader=False)