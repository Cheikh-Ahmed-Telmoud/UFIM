from django.contrib import admin
from .models import Workflow, WorkflowStep, WorkflowStepBranch

class WorkflowStepBranchInline(admin.TabularInline):
    model = WorkflowStepBranch
    fk_name = 'step'
    extra = 1

@admin.register(WorkflowStep)
class WorkflowStepAdmin(admin.ModelAdmin):
    list_display = ('name', 'workflow', 'step_type', 'variable_name', 'next_step_default', 'step_order')
    list_filter = ('step_type', 'workflow')
    search_fields = ('name', 'variable_name')
    inlines = [WorkflowStepBranchInline]
    ordering = ('workflow', 'step_order')

class WorkflowStepInline(admin.TabularInline):
    model = WorkflowStep
    extra = 1
    show_change_link = True
    fields = ('name', 'step_type', 'prompt_texts', 'variable_name', 'next_step_default', 'step_order')

@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'service', 'start_step', 'created_at')
    search_fields = ('service__name', 'service__institution__name')
    inlines = [WorkflowStepInline]
