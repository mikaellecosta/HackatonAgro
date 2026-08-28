import mimetypes

from django.http import FileResponse, Http404, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView

from core.services.diagnostico import DiagnosticInferenceError, get_diagnostic_image_path, get_diagnostic_job, submit_diagnostic


class DiagnosticoCreateView(LoginRequiredMixin, View):
    """Tela para iniciar um diagnóstico por imagem."""

    template_name = 'core/diagnostico/novo.html'

    def get(self, request, *args, **kwargs):
        return self.render_template(request)

    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist('images') or request.FILES.getlist('image')
        if not images:
            return JsonResponse({'error': 'Envie ao menos uma imagem.'}, status=400)
        try:
            job_id = submit_diagnostic(images)
        except DiagnosticInferenceError as exc:
            return JsonResponse({'error': str(exc)}, status=503)
        task_ids = request.session.get('diagnostic_jobs', [])
        request.session['diagnostic_jobs'] = [job_id, *task_ids[:9]]
        return JsonResponse({'job_id': job_id, 'redirect_url': '/diagnosticos/'}, status=202)

    def render_template(self, request):
        from django.shortcuts import render
        return render(request, self.template_name)


class DiagnosticoListView(LoginRequiredMixin, TemplateView):
    """Tela inicial para acompanhar diagnósticos e iniciar uma nova análise."""

    template_name = 'core/diagnostico/lista.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        jobs = []
        for job_id in self.request.session.get('diagnostic_jobs', []):
            data = get_diagnostic_job(job_id)
            if data:
                jobs.append({'id': job_id, 'data': data})
        context['diagnostic_jobs'] = jobs
        return context


class DiagnosticoStatusView(LoginRequiredMixin, View):
    def get(self, request, job_id):
        if job_id not in request.session.get('diagnostic_jobs', []):
            return JsonResponse({'error': 'Diagnóstico não encontrado.'}, status=404)
        job = get_diagnostic_job(job_id)
        if not job:
            return JsonResponse({'error': 'Diagnóstico expirado.'}, status=404)
        return JsonResponse(job)


class DiagnosticoImageView(LoginRequiredMixin, View):
    def get(self, request, job_id, filename):
        if job_id not in request.session.get('diagnostic_jobs', []):
            raise Http404
        image_path = get_diagnostic_image_path(job_id, filename)
        if not image_path:
            raise Http404
        content_type = mimetypes.guess_type(image_path.name)[0] or 'application/octet-stream'
        return FileResponse(image_path.open('rb'), content_type=content_type)
