<div class="mb-3 col-12 col-md-6">
    <label>__name_upper__s</label>
    @foreach ($__name__s as $__name__)
        <label class="L-tag">{{ $__name__->__first_col__ }}</label>
        <input type="checkbox" name="__name__s[]" value="{{ $__name__->id }}"##__model_lower__?? {{ $__model_lower__->__name__s->contains($__name__) ? "checked" : "" }}##>
    @endforeach
</div>