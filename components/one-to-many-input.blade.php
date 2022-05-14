<div class="mb-3 col-12 col-md-6">
    <label for="__name__" class="form-label">__name_upper__</label>
    <select name="__name__" id="__name__">
        @foreach ($__other_model_lower__s as $__other_model_lower__)
            <option value="{{ $__other_model_lower__->id }}"##__model_lower__?? {{ $__other_model_lower__->id == $__model_lower__->__name__ ? 'selected' : '' }}##>{{ $__other_model_lower__->__first_col__ }}</option>
        @endforeach
    </select>
</div>