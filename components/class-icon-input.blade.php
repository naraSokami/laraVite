<div class="mb-3 col-12 col-md-6">
    <label for="__name__" class="form-label">__name_upper__</label>
    <div class="L-radio-container">
        @foreach ($__icon_list__s as $__icon_list__)
            <div class="L-radio-item">
                <i class="{{ $__icon_list__->icon }}"></i>
                <input type=radio value="{{ $__icon_list__->icon }}" name="__name__"##__model_lower__?? {{ $__icon_list__->icon == $__model_lower__->__name__ ? "checked" : "" }}##>
            </div>
        @endforeach
    </div>
</div>