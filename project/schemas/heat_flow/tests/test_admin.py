from django.urls import reverse

from heat_flow.models import HeatFlow


class TestHeatFlowAdmin:
    def test_changelist(self, admin_client):
        url = reverse("admin:ghfdb_heatflow_changelist")
        response = admin_client.get(url)
        assert response.status_code == 200

    def test_search(self, admin_client):
        url = reverse("admin:ghfdb_heatflow_changelist")
        response = admin_client.get(url, data={"q": "test"})
        assert response.status_code == 200

    def test_add(self, admin_client):
        url = reverse("admin:ghfdb_heatflow_add")
        response = admin_client.get(url)
        assert response.status_code == 200

        # response = admin_client.post(
        #     url,
        #     data={
        #         "username": "test",
        #         "password1": "My_R@ndom-P@ssw0rd",
        #         "password2": "My_R@ndom-P@ssw0rd",
        #     },
        # )
        # assert response.status_code == 302
        # assert User.objects.filter(username="test").exists()

    def test_view_object(self, admin_client):
        pass
        # user = HeatFlow.objects.get(username="admin")
        # url = reverse("admin:users_user_change", kwargs={"object_id": user.pk})
        # response = admin_client.get(url)
        # assert response.status_code == 200
