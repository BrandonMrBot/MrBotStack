from {{ cookiecutter.project_name }}.views.classes import PrivateView


class Dashboard_view(PrivateView):
    def process_view(self):
        user_id = self.request.matchdict["userid"]

        return {
            "userid": user_id,
            "sectionActive": "dashboard",
        }
