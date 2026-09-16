{{- define "fedbox-codeserver.mode" -}}
{{- default "standard" .Values.mode -}}
{{- end -}}

{{- define "fedbox-codeserver.runtimeClassName" -}}
{{- if hasKey .Values "runtimeClassName" -}}
{{- .Values.runtimeClassName -}}
{{- else if eq (include "fedbox-codeserver.mode" .) "codejail" -}}
kata-clh-runtime-rs
{{- end -}}
{{- end -}}

{{- define "fedbox-codeserver.authEnabled" -}}
{{- if hasKey .Values "authEnabled" -}}
{{- .Values.authEnabled -}}
{{- else -}}
false
{{- end -}}
{{- end -}}

{{- define "fedbox-codeserver.storageMode" -}}
{{- if hasKey .Values.containersStorage "mode" -}}
{{- .Values.containersStorage.mode -}}
{{- else if eq (include "fedbox-codeserver.mode" .) "codejail" -}}
block
{{- else -}}
loopback
{{- end -}}
{{- end -}}

{{- define "fedbox-codeserver.privileged" -}}
{{- if hasKey .Values "privileged" -}}
{{- .Values.privileged -}}
{{- else -}}
{{- eq (include "fedbox-codeserver.mode" .) "codejail" -}}
{{- end -}}
{{- end -}}

{{- define "fedbox-codeserver.networkPolicyEnabled" -}}
{{- if hasKey .Values.networkPolicy "enabled" -}}
{{- .Values.networkPolicy.enabled -}}
{{- else -}}
{{- eq (include "fedbox-codeserver.mode" .) "codejail" -}}
{{- end -}}
{{- end -}}

{{- define "fedbox-codeserver.remoteSshEnabled" -}}
{{- if eq (toString .Values.remoteSsh.enabled) "true" -}}
true
{{- else -}}
false
{{- end -}}
{{- end -}}

{{- define "fedbox-codeserver.serviceSuffix" -}}
{{- if eq (include "fedbox-codeserver.mode" .) "codejail" -}}codejail{{- else -}}code-server{{- end -}}
{{- end -}}

{{- define "fedbox-codeserver.labelsInstance" -}}
{{- if eq (include "fedbox-codeserver.mode" .) "codejail" -}}codejail{{- else -}}code-server{{- end -}}
{{- end -}}