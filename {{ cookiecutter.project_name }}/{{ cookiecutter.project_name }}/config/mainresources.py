import os

import {{ cookiecutter.project_name }}.resources as r


def create_resources(apppath, config):
    r.add_library("main_library", os.path.join(apppath, "jsandcss"), config)

    # ----------------------------Basic CSS-----------------------
    r.add_css_resource(
        "main_library", "font-awesome", "plugins/fontawesome-free/css/all.min.css"
    )
    r.add_css_resource("main_library", "adminlte", "css/adminlte.min.css")

    r.add_css_resource("main_library", "toastr", "plugins/toastr/toastr.css")
    r.add_css_resource(
        "main_library", "sweetalert", "plugins/sweetalert/sweetalert.css"
    )
    r.add_css_resource(
        "main_library",
        "bootstrap-slider",
        "plugins/bootstrap-slider/css/bootstrap-slider.css",
    )
    r.add_css_resource(
        "main_library",
        "bootstrap-switch",
        "plugins/bootstrap-switch/css/bootstrap3/bootstrap-switch.min.css",
    )
    r.add_css_resource(
        "main_library",
        "select2",
        "plugins/select2/css/select2.min.css",
    )
    r.add_css_resource(
        "main_library",
        "icheck-bootstrap",
        "plugins/icheck-bootstrap/icheck-bootstrap.min.css",
    )
    r.add_css_resource(
        "main_library",
        "daterangepicker",
        "plugins/daterangepicker/daterangepicker.css",
    )

    r.add_css_resource(
        "main_library",
        "tempusdominus",
        "plugins/tempusdominus-bootstrap-4/css/tempusdominus-bootstrap-4.min.css",
    )

    r.add_css_resource(
        "main_library",
        "fullcalendar",
        "plugins/fullcalendar/main.css",
    )

    r.add_css_resource(
        "main_library",
        "datatablesbs4",
        "plugins/datatables-bs4/css/dataTables.bootstrap4.min.css",
    )
    r.add_css_resource(
        "main_library",
        "datatablesresponsive",
        "plugins/datatables-responsive/css/responsive.bootstrap4.min.css",
    )
    r.add_css_resource(
        "main_library",
        "datatablesbuttons",
        "plugins/datatables-buttons/css/buttons.bootstrap4.min.css",
    )
    r.add_css_resource(
        "main_library",
        "tour",
        "plugins/bootstrap-tour/css/bootstrap-tour-standalone.css",
    )

    # ----------------------------Basic JS----------------------------------------------------
    r.add_js_resource("main_library", "jquery", "plugins/jquery/jquery-3.5.1.min.js")
    r.add_js_resource(
        "main_library", "popper", "plugins/popper/popper.min.js", "jquery"
    )
    r.add_js_resource(
        "main_library", "bootstrap", "plugins/bootstrap/js/bootstrap-4.1.3.js", "popper"
    )
    r.add_js_resource("main_library", "adminlte", "js/adminlte.min.js")

    r.add_js_resource(
        "main_library", "toastr", "plugins/toastr/toastr.min.js", "jquery"
    )
    r.add_js_resource(
        "main_library", "sweetalert", "plugins/sweetalert/sweetalert.min.js", "jquery"
    )
    r.add_js_resource(
        "main_library",
        "jquery-knob",
        "plugins/jquery-knob/jquery.knob.min.js",
        "jquery",
    )
    r.add_js_resource(
        "main_library",
        "jqueryvalidate",
        "plugins/jquery-validation/jquery.validate.min.js",
        "jquery",
    )
    r.add_js_resource(
        "main_library",
        "jquerymethods",
        "plugins/jquery-validation/additional-methods.min.js",
        "jquery",
    )
    r.add_js_resource(
        "main_library",
        "bootstrap-slider",
        "plugins/bootstrap-slider/bootstrap-slider.min.js",
        "jquery",
    )
    r.add_js_resource(
        "main_library",
        "bootstrap-switch",
        "plugins/bootstrap-switch/js/bootstrap-switch.min.js",
        "jquery",
    )
    r.add_js_resource(
        "main_library",
        "select2",
        "plugins/select2/js/select2.full.min.js",
        "jquery",
    )
    r.add_js_resource(
        "main_library",
        "Chart",
        "plugins/chart.js/Chart.min.js",
        "jquery",
    )
    r.add_js_resource(
        "main_library",
        "moment",
        "plugins/moment/moment.min.js",
        "jquery",
    )
    r.add_js_resource(
        "main_library",
        "daterangepicker",
        "plugins/daterangepicker/daterangepicker.js",
        "moment",
    )
    r.add_js_resource(
        "main_library",
        "jquery-ui",
        "plugins/jquery-ui/jquery-ui.min.js",
        "moment",
    )
    r.add_js_resource(
        "main_library",
        "tempusdominus",
        "plugins/tempusdominus-bootstrap-4/js/tempusdominus-bootstrap-4.min.js",
        "moment",
    )

    r.add_js_resource(
        "main_library",
        "fullcalendar",
        "plugins/fullcalendar/main.js",
        "jquery-ui",
    )

    r.add_js_resource(
        "main_library",
        "datatables",
        "plugins/datatables/jquery.dataTables.min.js",
        "jquery-ui",
    )
    r.add_js_resource(
        "main_library",
        "datatables-bs4",
        "plugins/datatables-bs4/js/dataTables.bootstrap4.min.js",
        "datatables",
    )
    r.add_js_resource(
        "main_library",
        "datatablesresponsive",
        "plugins/datatables-responsive/js/dataTables.responsive.min.js",
        "datatables-bs4",
    )
    r.add_js_resource(
        "main_library",
        "datatablesresponsive2",
        "plugins/datatables-responsive/js/responsive.bootstrap4.min.js",
        "datatablesresponsive",
    )
    r.add_js_resource(
        "main_library",
        "tour",
        "plugins/bootstrap-tour/bootstrap-tour-standalone.min.js",
        "bootstrap",
    )
