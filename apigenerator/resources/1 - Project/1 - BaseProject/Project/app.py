# Infra Imports #
import src.e_Infra.g_Environment.EnvironmentVariables

# Controller Imports #
import src.a_Presentation.d_Swagger.SwaggerController
import src.a_Presentation.f_Redoc.RedocController
import src.a_Presentation.b_Custom.FlaskAdminPanelController
import src.a_Presentation.b_Custom.OptionsController
# import src.a_Presentation.b_Custom.SQLController # Removed as the file does not exist
import src.a_Presentation.b_Custom.BeforeRequestController
import src.a_Presentation.b_Custom.ExceptionHandlerController

# Assuming app_handler is central and likely from FlaskBuilder
# This import is added to ensure app_handler is available for the __main__ block
from src.e_Infra.b_Builders.FlaskBuilder import app_handler

# LocalHost run #
if __name__ == "__main__":
    app_handler.run(debug=True, use_reloader=False)